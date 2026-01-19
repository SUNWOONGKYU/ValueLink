// bridge_server.js - Human-ClaudeCode Bridge 서버
// Order Sheet를 Orders/에 저장, Reports/ 파일 제공

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

const app = express();
const PORT = 3030;

// CORS 설정 (모든 출처 허용)
app.use(cors());

// JSON 요청 본문 파싱
app.use(express.json({ limit: '10mb' }));

// Orders 디렉토리 경로
const ORDERS_DIR = path.join(__dirname, 'Orders');

// Orders 디렉토리가 없으면 생성
if (!fs.existsSync(ORDERS_DIR)) {
    fs.mkdirSync(ORDERS_DIR, { recursive: true });
}

// Reports 디렉토리 경로
const REPORTS_DIR = path.join(__dirname, 'Reports');

// Reports 디렉토리가 없으면 생성
if (!fs.existsSync(REPORTS_DIR)) {
    fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

// Health check 엔드포인트
app.get('/ping', (req, res) => {
    res.json({ status: 'ok', message: 'Bridge server is running' });
});

// 파일 저장 엔드포인트
app.post('/save', (req, res) => {
    try {
        const { content, filename, targetPath } = req.body;

        if (!content) {
            return res.status(400).json({
                success: false,
                error: '내용이 비어있습니다.'
            });
        }

        // 파일명 생성 (제공되지 않으면 타임스탬프 사용)
        let finalFilename = filename;
        if (!finalFilename) {
            const timestamp = new Date().toISOString()
                .slice(0, 19)
                .replace(/:/g, '-')
                .replace('T', '_');
            finalFilename = `order_${timestamp}.json`;
        }

        // .json 확장자가 없으면 추가
        if (!finalFilename.endsWith('.json')) {
            finalFilename += '.json';
        }

        // 대상 디렉토리 결정 (targetPath가 있으면 사용, 없으면 기본 ORDERS_DIR)
        let targetDir = ORDERS_DIR;
        if (targetPath) {
            targetDir = targetPath;
            // 대상 디렉토리가 없으면 생성
            if (!fs.existsSync(targetDir)) {
                fs.mkdirSync(targetDir, { recursive: true });
                console.log(`📁 디렉토리 생성: ${targetDir}`);
            }
        }

        // 파일 경로
        const filePath = path.join(targetDir, finalFilename);

        // 파일 저장
        fs.writeFileSync(filePath, content, 'utf8');

        console.log(`✅ 파일 저장 완료: ${finalFilename}`);
        console.log(`📂 저장 경로: ${filePath}`);

        res.json({
            success: true,
            filename: finalFilename,
            path: filePath,
            message: `파일이 ${targetDir}에 저장되었습니다.`
        });

    } catch (error) {
        console.error('❌ 파일 저장 실패:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Order Sheet 저장 (MD 파일용)
// 레거시 엔드포인트: 호환성을 위해 유지
app.post('/save-order', (req, res) => {
    try {
        const { content, filename } = req.body;

        if (!content) {
            return res.status(400).json({
                success: false,
                error: '내용이 비어있습니다.'
            });
        }

        // 파일명 생성 (제공되지 않으면 타임스탬프 사용)
        let finalFilename = filename;
        if (!finalFilename) {
            const timestamp = new Date().toISOString()
                .slice(0, 19)
                .replace(/:/g, '-')
                .replace('T', '_');
            finalFilename = `order_${timestamp}.md`;
        }

        // .md 확장자 보장
        if (!finalFilename.endsWith('.md') && !finalFilename.endsWith('.json')) {
            finalFilename += '.md';
        }

        // 파일 경로 (항상 Orders에 저장)
        const filePath = path.join(ORDERS_DIR, finalFilename);

        // 파일 저장
        fs.writeFileSync(filePath, content, 'utf8');

        console.log(`✅ Order Sheet 자동 발행 완료: ${finalFilename}`);
        console.log(`📂 저장 경로: ${filePath}`);

        res.json({
            success: true,
            filename: finalFilename,
            path: filePath,
            message: `Order Sheet가 Orders에 저장되었습니다.`
        });

    } catch (error) {
        console.error('❌ Order Sheet 자동 발행 실패:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// 저장된 파일 목록 조회
app.get('/files', (req, res) => {
    try {
        const files = fs.readdirSync(ORDERS_DIR)
            .filter(file => file.endsWith('.md') || file.endsWith('.json'))
            .map(file => {
                const filePath = path.join(ORDERS_DIR, file);
                const stats = fs.statSync(filePath);
                return {
                    filename: file,
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime,
                    type: file.endsWith('.md') ? 'markdown' : 'json'
                };
            })
            .sort((a, b) => b.modified - a.modified);

        res.json({
            success: true,
            count: files.length,
            files
        });

    } catch (error) {
        console.error('❌ 파일 목록 조회 실패:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Reports 파일 목록 조회
app.get('/reports', (req, res) => {
    try {
        const files = fs.readdirSync(REPORTS_DIR)
            .filter(file => file.endsWith('.json') || file.endsWith('.md'))
            .map(file => {
                const filePath = path.join(REPORTS_DIR, file);
                const stats = fs.statSync(filePath);
                return {
                    filename: file,
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime,
                    type: file.endsWith('.md') ? 'markdown' : 'json'
                };
            })
            .sort((a, b) => b.modified - a.modified);

        res.json({
            success: true,
            count: files.length,
            files
        });

    } catch (error) {
        console.error('❌ Reports 파일 목록 조회 실패:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Reports 파일 읽기
app.get('/report/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const filePath = path.join(REPORTS_DIR, filename);

        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                error: '파일을 찾을 수 없습니다.'
            });
        }

        let content = fs.readFileSync(filePath, 'utf8');
        let contentType = 'json';

        // .md 파일이면 HTML로 변환
        if (filename.endsWith('.md')) {
            contentType = 'markdown';
            const htmlContent = marked.parse(content);

            // JSON으로 감싸서 반환 (대시보드와 호환)
            content = JSON.stringify({
                type: 'markdown',
                title: filename.replace('.md', ''),
                date: new Date().toISOString().split('T')[0],
                content: htmlContent
            });
        }

        // 파일 읽기만 함 (Archive 이동은 별도 엔드포인트로)
        res.json({
            success: true,
            filename: filename,
            content: content,
            type: contentType
        });

    } catch (error) {
        console.error('❌ Reports 파일 읽기 실패:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ============================================
// 📁 Archive 이동 엔드포인트
// ============================================

const REPORTS_ARCHIVE_DIR = path.join(REPORTS_DIR, 'Archive');
const ORDERS_ARCHIVE_DIR = path.join(ORDERS_DIR, 'Archive');

// Reports 파일을 Archive로 이동
app.post('/archive/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        archiveReportFile(filename);
        res.json({
            success: true,
            message: `${filename}이(가) Archive로 이동되었습니다.`
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

function archiveReportFile(filename) {
    // Archive 폴더 생성
    if (!fs.existsSync(REPORTS_ARCHIVE_DIR)) {
        fs.mkdirSync(REPORTS_ARCHIVE_DIR, { recursive: true });
    }

    const srcPath = path.join(REPORTS_DIR, filename);
    const destPath = path.join(REPORTS_ARCHIVE_DIR, filename);

    // 파일이 존재하는지 확인
    if (!fs.existsSync(srcPath)) {
        return;
    }

    try {
        fs.renameSync(srcPath, destPath);
        console.log(`📁 [ARCHIVE] Reports → Archive: ${filename}`);

        // 관련 파일들도 이동 (_ack, _final 등)
        const baseName = filename.replace(/_final\.json$|_ack\.json$|\.json$|\.md$/, '');
        const relatedFiles = fs.readdirSync(REPORTS_DIR).filter(f => f.startsWith(baseName));

        relatedFiles.forEach(relatedFile => {
            const relatedSrc = path.join(REPORTS_DIR, relatedFile);
            const relatedDest = path.join(REPORTS_ARCHIVE_DIR, relatedFile);
            if (fs.existsSync(relatedSrc)) {
                fs.renameSync(relatedSrc, relatedDest);
                console.log(`📁 [ARCHIVE] Reports → Archive: ${relatedFile}`);
            }
        });

        // 원본 Orders 파일도 Archive로 이동
        archiveOrderFile(baseName);

    } catch (err) {
        console.log(`⚠️  Archive 이동 실패: ${err.message}`);
    }
}

function archiveOrderFile(baseName) {
    // Archive 폴더 생성
    if (!fs.existsSync(ORDERS_ARCHIVE_DIR)) {
        fs.mkdirSync(ORDERS_ARCHIVE_DIR, { recursive: true });
    }

    // Orders에서 관련 파일 찾기
    try {
        const orderFiles = fs.readdirSync(ORDERS_DIR).filter(f =>
            f.endsWith('.json') && !f.startsWith('.')
        );

        orderFiles.forEach(orderFile => {
            const orderPath = path.join(ORDERS_DIR, orderFile);
            try {
                const content = fs.readFileSync(orderPath, 'utf8');
                const order = JSON.parse(content);
                const orderId = order.order_id || order.task_id || '';

                // Order ID가 baseName에 포함되어 있으면 이동
                if (baseName.includes(orderId)) {
                    const destPath = path.join(ORDERS_ARCHIVE_DIR, orderFile);
                    fs.renameSync(orderPath, destPath);
                    console.log(`📁 [ARCHIVE] Orders → Archive: ${orderFile}`);
                }
            } catch (e) {
                // 파싱 실패 시 무시
            }
        });
    } catch (err) {
        // 조용히 실패
    }
}

// 서버 시작
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🌉 Human-ClaudeCode Bridge Server 실행 중           ║
║                                                       ║
║   포트: ${PORT}                                        ║
║   Orders 경로: ${ORDERS_DIR}
║   Reports 경로: ${REPORTS_DIR}
║                                                       ║
║   API 엔드포인트:                                      ║
║   - GET  /ping                 서버 상태 확인         ║
║   - POST /save                 Order 저장 (JSON)      ║
║   - POST /save-order           Order 저장 (MD)        ║
║   - GET  /files                Orders 목록            ║
║   - GET  /reports              Reports 목록           ║
║   - GET  /report/:file         Report 읽기            ║
║   - POST /archive/:file        Archive 이동           ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    `);
});

// 에러 핸들링
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
});

process.on('unhandledRejection', (error) => {
    console.error('❌ Unhandled Rejection:', error);
});
