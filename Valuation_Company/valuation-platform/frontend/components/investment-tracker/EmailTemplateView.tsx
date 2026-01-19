'use client';

/**
 * Email Template View Component
 * 이메일 템플릿 뷰어/편집 컴포넌트
 */
import { useState } from 'react';
import { EmailTemplate } from '@/lib/api/investment-tracker';

interface Props {
  template: EmailTemplate | null;
  onRegenerate?: (feedback?: string) => Promise<void>;
  loading?: boolean;
}

export default function EmailTemplateView({ template, onRegenerate, loading }: Props) {
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  const handleRegenerate = async () => {
    if (!onRegenerate) return;

    setRegenerating(true);
    try {
      await onRegenerate(showFeedback ? feedback : undefined);
      setFeedback('');
      setShowFeedback(false);
    } finally {
      setRegenerating(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('복사되었습니다.');
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>
    );
  }

  if (!template) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        <p>이메일 템플릿이 없습니다.</p>
        {onRegenerate && (
          <button
            onClick={() => handleRegenerate()}
            disabled={regenerating}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {regenerating ? '생성 중...' : '이메일 생성하기'}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* 헤더 */}
      <div className="bg-gray-50 px-6 py-4 border-b flex items-center justify-between">
        <div>
          <h3 className="font-medium text-gray-900">이메일 템플릿</h3>
          <p className="text-xs text-gray-500 mt-1">
            버전 {template.version} | {template.template_type === 'initial' ? '초기 접촉' : '후속'} |
            생성일: {new Date(template.created_at).toLocaleDateString('ko-KR')}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => copyToClipboard(`${template.subject}\n\n${template.body}`)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            복사
          </button>
          {onRegenerate && (
            <button
              onClick={() => setShowFeedback(!showFeedback)}
              className="px-3 py-1.5 text-sm border border-blue-500 text-blue-600 rounded hover:bg-blue-50"
            >
              재생성
            </button>
          )}
        </div>
      </div>

      {/* 피드백 입력 */}
      {showFeedback && (
        <div className="px-6 py-4 bg-blue-50 border-b">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            수정 요청 (선택사항)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="예: 좀 더 캐주얼하게, 가치 제안을 강조해서..."
            className="w-full p-2 border rounded-lg text-sm"
            rows={2}
          />
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {regenerating ? '생성 중...' : '새로 생성하기'}
          </button>
        </div>
      )}

      {/* 이메일 내용 */}
      <div className="p-6">
        {/* 제목 */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-500 mb-1">제목</label>
          <div className="p-3 bg-gray-50 rounded-lg font-medium">
            {template.subject}
          </div>
        </div>

        {/* 본문 */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">본문</label>
          <div className="p-4 bg-gray-50 rounded-lg whitespace-pre-wrap text-sm leading-relaxed">
            {template.body}
          </div>
        </div>
      </div>
    </div>
  );
}
