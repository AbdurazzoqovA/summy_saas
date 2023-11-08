document.getElementById('input-file').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    const neighbourPanel = document.querySelector('.neighbourPanel');

    if (file.type === 'application/pdf') {
        // Handle PDF file
        const fileReader = new FileReader();
        fileReader.onload = function() {
            const typedarray = new Uint8Array(this.result);

            pdfjsLib.getDocument(typedarray).promise.then(pdf => {
                let text = '';
                for (let i = 1; i <= pdf.numPages; i++) {
                    pdf.getPage(i).then(page => {
                        page.getTextContent().then(content => {
                            content.items.forEach(item => {
                                text += item.str + ' ';
                            });

                            if (i === pdf.numPages) {
                                neighbourPanel.textContent = text;
                            }
                        });
                    });
                }
            });
        };
        fileReader.readAsArrayBuffer(file);
    } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        // Handle Word file (.docx)
        const fileReader = new FileReader();
        fileReader.onload = function(event) {
            const arrayBuffer = event.target.result;

            mammoth.extractRawText({ arrayBuffer: arrayBuffer })
                .then(result => {
                    neighbourPanel.textContent = result.value;
                })
                .catch(err => {
                    console.error('Error reading .docx file:', err);
                });
        };
        fileReader.readAsArrayBuffer(file);
    } else {
        neighbourPanel.textContent = 'Unsupported file type.';
    }
});
