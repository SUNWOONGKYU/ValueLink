/**
 * @task S2BA4
 * @description AI integrated client - Claude, Gemini, GPT
 *
 * 50:30:20 hybrid strategy implementation
 * Claude 50% (Opus 4.6 - Feb 2026) - DCF calculation, code review, security review
 * Gemini 20% (3.1 Pro - Latest Feb 2026) - Large document analysis, company research, industry analysis
 * OpenAI 30% (GPT-5.2 - Latest Feb 2026) - PDF analysis, image OCR, Excel formula, chatbot
 */

// ---------------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------------

/** Supported AI provider identifiers */
type AIProvider = 'claude' | 'gemini' | 'gpt';

/** A single message in a conversation */
interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

/** Standardised response returned by every provider call */
interface AIResponse {
  content: string;
  provider: AIProvider;
  tokens_used?: number;
  cached?: boolean;
  latency_ms?: number;
}

/** Client-level configuration */
interface AIConfig {
  maxRetries: number;
  timeout: number;
  /** Cache time-to-live in milliseconds */
  cacheTTL: number;
}

/** Optional overrides passed to `chat()` */
interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  /** When true the response will not be written to the cache */
  skipCache?: boolean;
}

/** Internal cache entry */
interface CacheEntry {
  response: AIResponse;
  expiresAt: number;
}

/** Token usage tracked per provider */
interface TokenUsage {
  totalTokens: number;
  requestCount: number;
}

/** Simple sliding-window rate-limit state */
interface RateLimitState {
  /** Maximum requests allowed per window */
  maxRequests: number;
  /** Window duration in milliseconds */
  windowMs: number;
  /** Timestamps of requests inside the current window */
  timestamps: number[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: AIConfig = {
  maxRetries: 3,
  timeout: 30_000,
  cacheTTL: 5 * 60 * 1000, // 5 minutes
};

const CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages';
const GEMINI_API_URL =
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro:generateContent';
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

// ---------------------------------------------------------------------------
// AIClient
// ---------------------------------------------------------------------------

/**
 * Unified AI client supporting Claude, Gemini and GPT-4.
 *
 * All provider calls go through the native `fetch` API (no SDK dependencies).
 * Features: retry with exponential back-off, response caching, token tracking
 * and simple rate limiting.
 *
 * @example
 * ```ts
 * const client = new AIClient();
 * const res = await client.chat('claude', [
 *   { role: 'user', content: 'Explain DCF valuation.' }
 * ]);
 * console.log(res.content);
 * ```
 */
class AIClient {
  private config: AIConfig;
  private cache: Map<string, CacheEntry> = new Map();
  private tokenUsage: Map<AIProvider, TokenUsage> = new Map();
  private rateLimits: Map<AIProvider, RateLimitState> = new Map();

  constructor(config?: Partial<AIConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };

    // Initialise token usage counters
    for (const provider of ['claude', 'gemini', 'gpt'] as AIProvider[]) {
      this.tokenUsage.set(provider, { totalTokens: 0, requestCount: 0 });
    }

    // Initialise rate limiters (defaults: 60 req / 60 s)
    for (const provider of ['claude', 'gemini', 'gpt'] as AIProvider[]) {
      this.rateLimits.set(provider, {
        maxRequests: 60,
        windowMs: 60_000,
        timestamps: [],
      });
    }
  }

  // -----------------------------------------------------------------------
  // Public API
  // -----------------------------------------------------------------------

  /**
   * Unified chat interface - routes the request to the chosen provider.
   *
   * @param provider - Which AI provider to use
   * @param messages - Conversation messages
   * @param options  - Optional overrides (temperature, maxTokens, skipCache)
   * @returns A standardised {@link AIResponse}
   */
  async chat(
    provider: AIProvider,
    messages: AIMessage[],
    options?: ChatOptions,
  ): Promise<AIResponse> {
    this.validateEnvVars(provider);
    this.enforceRateLimit(provider);

    // Cache lookup
    const cacheKey = this.buildCacheKey(provider, messages);
    if (!options?.skipCache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) return { ...cached, cached: true };
    }

    const start = Date.now();
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        const response = await this.callProvider(provider, messages, options);
        const latency = Date.now() - start;
        const result: AIResponse = { ...response, latency_ms: latency };

        // Store in cache
        if (!options?.skipCache) {
          this.setCache(cacheKey, result);
        }

        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        // Only retry on transient / server errors
        if (attempt < this.config.maxRetries) {
          const backoff = Math.min(1000 * Math.pow(2, attempt - 1), 8000);
          await this.sleep(backoff);
        }
      }
    }

    throw new Error(
      `[AIClient] ${provider} failed after ${this.config.maxRetries} retries: ${lastError?.message}`,
    );
  }

  /**
   * Send a request to the Claude API.
   *
   * @param messages - Conversation messages
   * @param options  - Optional overrides
   * @returns An {@link AIResponse} from Claude
   */
  async callClaude(
    messages: AIMessage[],
    options?: ChatOptions,
  ): Promise<AIResponse> {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('[AIClient] ANTHROPIC_API_KEY is not set');

    // Separate system message (Anthropic uses a top-level `system` field)
    const systemMsg = messages.find((m) => m.role === 'system');
    const nonSystemMsgs = messages.filter((m) => m.role !== 'system');

    const body: Record<string, unknown> = {
      model: 'claude-opus-4-6',
      max_tokens: options?.maxTokens ?? 4096,
      messages: nonSystemMsgs.map((m) => ({ role: m.role, content: m.content })),
    };
    if (systemMsg) {
      body.system = systemMsg.content;
    }
    if (options?.temperature !== undefined) {
      body.temperature = options.temperature;
    }

    const res = await this.fetchWithTimeout(CLAUDE_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Claude API error ${res.status}: ${text}`);
    }

    const data = await res.json();
    const content: string = data.content?.[0]?.text ?? '';
    const tokensUsed: number =
      (data.usage?.input_tokens ?? 0) + (data.usage?.output_tokens ?? 0);

    this.trackTokens('claude', tokensUsed);

    return { content, provider: 'claude', tokens_used: tokensUsed };
  }

  /**
   * Send a request to the Gemini API.
   *
   * @param messages - Conversation messages
   * @param options  - Optional overrides
   * @returns An {@link AIResponse} from Gemini
   */
  async callGemini(
    messages: AIMessage[],
    options?: ChatOptions,
  ): Promise<AIResponse> {
    const apiKey = process.env.GOOGLE_AI_API_KEY;
    if (!apiKey) throw new Error('[AIClient] GOOGLE_AI_API_KEY is not set');

    // Gemini expects `contents` with role `user` / `model`
    const contents = messages
      .filter((m) => m.role !== 'system')
      .map((m) => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }],
      }));

    // Prepend system instruction as a user message if present
    const systemMsg = messages.find((m) => m.role === 'system');
    if (systemMsg) {
      contents.unshift({
        role: 'user',
        parts: [{ text: `[System Instruction] ${systemMsg.content}` }],
      });
    }

    const body: Record<string, unknown> = {
      contents,
      generationConfig: {
        maxOutputTokens: options?.maxTokens ?? 4096,
        ...(options?.temperature !== undefined
          ? { temperature: options.temperature }
          : {}),
      },
    };

    const url = `${GEMINI_API_URL}?key=${apiKey}`;
    const res = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Gemini API error ${res.status}: ${text}`);
    }

    const data = await res.json();
    const content: string =
      data.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
    const tokensUsed: number =
      (data.usageMetadata?.promptTokenCount ?? 0) +
      (data.usageMetadata?.candidatesTokenCount ?? 0);

    this.trackTokens('gemini', tokensUsed);

    return { content, provider: 'gemini', tokens_used: tokensUsed };
  }

  /**
   * Send a request to the OpenAI Chat Completions API.
   *
   * @param messages - Conversation messages
   * @param options  - Optional overrides
   * @returns An {@link AIResponse} from GPT
   */
  async callGPT(
    messages: AIMessage[],
    options?: ChatOptions,
  ): Promise<AIResponse> {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('[AIClient] OPENAI_API_KEY is not set');

    const body: Record<string, unknown> = {
      model: 'gpt-5.2',
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      max_tokens: options?.maxTokens ?? 4096,
    };
    if (options?.temperature !== undefined) {
      body.temperature = options.temperature;
    }

    const res = await this.fetchWithTimeout(OPENAI_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`OpenAI API error ${res.status}: ${text}`);
    }

    const data = await res.json();
    const content: string = data.choices?.[0]?.message?.content ?? '';
    const tokensUsed: number = data.usage?.total_tokens ?? 0;

    this.trackTokens('gpt', tokensUsed);

    return { content, provider: 'gpt', tokens_used: tokensUsed };
  }

  /**
   * Return cumulative token usage for a specific provider.
   *
   * @param provider - The provider to query
   * @returns Token usage statistics
   */
  getTokenUsage(provider: AIProvider): TokenUsage {
    return this.tokenUsage.get(provider) ?? { totalTokens: 0, requestCount: 0 };
  }

  /**
   * Return cumulative token usage for all providers.
   *
   * @returns A map of provider to token usage
   */
  getAllTokenUsage(): Record<AIProvider, TokenUsage> {
    return {
      claude: this.getTokenUsage('claude'),
      gemini: this.getTokenUsage('gemini'),
      gpt: this.getTokenUsage('gpt'),
    };
  }

  /**
   * Clear the entire response cache.
   */
  clearCache(): void {
    this.cache.clear();
  }

  // -----------------------------------------------------------------------
  // Private helpers
  // -----------------------------------------------------------------------

  /**
   * Route a request to the appropriate provider method.
   */
  private async callProvider(
    provider: AIProvider,
    messages: AIMessage[],
    options?: ChatOptions,
  ): Promise<AIResponse> {
    switch (provider) {
      case 'claude':
        return this.callClaude(messages, options);
      case 'gemini':
        return this.callGemini(messages, options);
      case 'gpt':
        return this.callGPT(messages, options);
      default:
        throw new Error(`[AIClient] Unsupported provider: ${provider}`);
    }
  }

  /**
   * Validate that the required environment variable for a provider is set.
   */
  private validateEnvVars(provider: AIProvider): void {
    const envMap: Record<AIProvider, string> = {
      claude: 'ANTHROPIC_API_KEY',
      gemini: 'GOOGLE_AI_API_KEY',
      gpt: 'OPENAI_API_KEY',
    };
    const key = envMap[provider];
    if (!process.env[key]) {
      throw new Error(`[AIClient] Environment variable ${key} is not set`);
    }
  }

  /**
   * `fetch` wrapper that aborts after the configured timeout.
   */
  private async fetchWithTimeout(
    url: string,
    init: RequestInit,
  ): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      return await fetch(url, { ...init, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * Record token consumption for a provider.
   */
  private trackTokens(provider: AIProvider, tokens: number): void {
    const usage = this.tokenUsage.get(provider);
    if (usage) {
      usage.totalTokens += tokens;
      usage.requestCount += 1;
    }
  }

  /**
   * Enforce the sliding-window rate limit for a provider.
   * Throws if the limit has been exceeded.
   */
  private enforceRateLimit(provider: AIProvider): void {
    const state = this.rateLimits.get(provider);
    if (!state) return;

    const now = Date.now();
    // Purge timestamps outside the window
    state.timestamps = state.timestamps.filter(
      (ts) => now - ts < state.windowMs,
    );

    if (state.timestamps.length >= state.maxRequests) {
      throw new Error(
        `[AIClient] Rate limit exceeded for ${provider}: ${state.maxRequests} requests per ${state.windowMs / 1000}s`,
      );
    }

    state.timestamps.push(now);
  }

  // -----------------------------------------------------------------------
  // Cache helpers
  // -----------------------------------------------------------------------

  /**
   * Build a deterministic cache key from provider + messages.
   */
  private buildCacheKey(provider: AIProvider, messages: AIMessage[]): string {
    const payload = JSON.stringify({ provider, messages });
    // Simple hash - good enough for in-memory dedup
    let hash = 0;
    for (let i = 0; i < payload.length; i++) {
      const ch = payload.charCodeAt(i);
      hash = ((hash << 5) - hash + ch) | 0;
    }
    return `${provider}:${hash}`;
  }

  /**
   * Retrieve a non-expired entry from the cache.
   */
  private getFromCache(key: string): AIResponse | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    return entry.response;
  }

  /**
   * Store a response in the cache with TTL.
   */
  private setCache(key: string, response: AIResponse): void {
    this.cache.set(key, {
      response,
      expiresAt: Date.now() + this.config.cacheTTL,
    });
  }

  /**
   * Promise-based sleep.
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

/** Pre-configured singleton AI client */
const aiClient = new AIClient();

export { AIClient, aiClient };
export type {
  AIProvider,
  AIMessage,
  AIResponse,
  AIConfig,
  ChatOptions,
  TokenUsage,
};
