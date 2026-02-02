#!/usr/bin/env python3
"""
가이드 파일들의 사이드바 스크립트를 간단하게 교체하는 스크립트
"""
import re

guides = {
    'guide-relative.html': 'relative',
    'guide-intrinsic.html': 'intrinsic',
    'guide-asset.html': 'asset',
    'guide-tax.html': 'inheritance_tax'
}

simple_script_template = '''    <!-- 사이드바 초기화 -->
    <script type="module">
        import {{ injectSidebar }} from '../../../components/common-sidebar.js';

        // 페이지 로드 시 사이드바 초기화 (로그인 체크 없이 바로 표시)
        injectSidebar(
            'sidebar-container',
            5,                  // 5단계 (평가 기초자료 제출)
            'approved',         // 상태: 승인됨
            '{method}',         // {method_name}
            null,               // 프로젝트 ID 없음
            5,                  // startStep: 5단계부터 (기초자료 제출부터)
            15                  // endStep: 15단계까지
        );
    </script>'''

for filename, method in guides.items():
    print(f"Processing {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 사이드바 스크립트 부분을 찾아서 교체
    # 패턴: <!-- 사이드바 및 상태 체크 --> 부터 다음 <script> 태그 전까지
    pattern = r'    <!-- 사이드바 및 상태 체크 -->.*?    </script>'

    method_name = method.replace('_', ' ').title()
    replacement = simple_script_template.format(method=method, method_name=method_name)

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 파일 저장
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Done: {filename}")

print("\n모든 파일 처리 완료!")
