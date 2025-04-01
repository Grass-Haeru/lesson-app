// PDF.jsライブラリの設定
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';

// フォームデータの送信処理
function submitForm() {
    // 生徒の情報を取得
    const studentCount = document.getElementById('studentCount').value;
    const studentLevel = document.getElementById('studentLevel').value;
    const grade = document.getElementById('grade').value;
    const subject = document.getElementById('subject').value;
    
    console.log('生徒の人数:', studentCount);
    console.log('学力:', studentLevel);
    console.log('学年:', grade);
    console.log('単元:', subject);
    
    // PDF ファイルの読み込み
    const pdfFile = document.getElementById('pdfFile').files[0];
    if (pdfFile) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const pdfData = event.target.result;
            displayPDF(pdfData); // PDF の表示
        };
        reader.readAsArrayBuffer(pdfFile);
    } else {
        alert('指導案PDFをアップロードしてください。');
    }
}

// PDF の表示
function displayPDF(pdfData) {
    const pdfContent = document.getElementById('pdfContent');
    pdfjsLib.getDocument({ data: pdfData }).promise.then(function(pdf) {
        pdf.getPage(1).then(function(page) {
            const scale = 1.5;
            const viewport = page.getViewport({ scale: scale });
            
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };
            
            page.render(renderContext).promise.then(function() {
                pdfContent.appendChild(canvas);
            });
        });
    });
}
