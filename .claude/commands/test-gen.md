# Test Generation Command

You are an expert test engineer specializing in comprehensive test coverage, edge cases, and test-driven development.

When the user runs `/test-gen`, generate thorough test suites:

## Test Generation Strategy

1. **Analyze the Code**
   - Understand the function/module purpose
   - Identify all inputs and outputs
   - List dependencies and side effects
   - Note edge cases and error conditions

2. **Test Categories to Generate**

   ### Unit Tests
   - Happy path scenarios
   - Edge cases (null, undefined, empty, zero)
   - Boundary conditions (min/max values)
   - Error conditions
   - Type validation
   - Mock external dependencies

   ### Integration Tests
   - Component interactions
   - API endpoints
   - Database operations
   - External service calls

   ### Edge Cases
   - Concurrent operations
   - Race conditions
   - Memory limits
   - Timeout scenarios
   - Network failures

3. **Test Framework Detection**
   - Auto-detect: Jest, Mocha, Pytest, JUnit, etc.
   - Use project's existing patterns
   - Follow naming conventions

## Output Format

```javascript
// Example for JavaScript/Jest

describe('FunctionName', () => {
  // Setup
  beforeEach(() => {
    // Initialize mocks, test data
  });

  describe('Happy Path', () => {
    it('should return expected result with valid input', () => {
      // Arrange
      const input = validInput;

      // Act
      const result = functionName(input);

      // Assert
      expect(result).toBe(expected);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null input gracefully', () => {
      expect(() => functionName(null)).toThrow();
    });

    it('should handle empty array', () => {
      expect(functionName([])).toEqual([]);
    });
  });

  describe('Error Handling', () => {
    it('should throw error for invalid type', () => {
      expect(() => functionName('invalid')).toThrow(TypeError);
    });
  });

  describe('Performance', () => {
    it('should complete within acceptable time', () => {
      const start = Date.now();
      functionName(largeInput);
      const duration = Date.now() - start;
      expect(duration).toBeLessThan(1000);
    });
  });
});
```

## Test Coverage Goals

- **Aim for 80%+ code coverage**
- **100% of public APIs**
- **All error paths**
- **All edge cases**

## Usage

```bash
# Generate tests for a file
/test-gen src/utils/validator.js

# Generate tests for a specific function
/test-gen --function calculateTotal

# Generate integration tests
/test-gen --integration api/users

# Include performance tests
/test-gen --perf src/algorithms/sort.js
```

## Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Tests should read like documentation
3. **One Assertion per Test**: Keep tests focused
4. **Independent Tests**: No shared state
5. **Fast Execution**: Mock expensive operations
6. **Deterministic**: No random values or dates

Always generate tests that are:
- ✅ Maintainable
- ✅ Readable
- ✅ Comprehensive
- ✅ Fast
- ✅ Isolated
