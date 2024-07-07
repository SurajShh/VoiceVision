let text = document.getElementById('text');
let leaf = document.getElementById('leaf');
let hill1 = document.getElementById('hill1');
let loadingBar = document.getElementById('loading-bar');

window.addEventListener('scroll', () => { 
    let value = window.scrollY;

text.style.marginTop = value * 2.5 + 'px';
leaf.style.top = value * -1.5 + 'px';
leaf.style.left = value * 1.5 + 'px';

});
function showLoadingBar() {
    loadingBar.style.display = 'block';
}

function hideLoadingBar() {
    loadingBar.style.display = 'none';
}

document.getElementById('generate-transcription').addEventListener('click', function() {
    const youtubeLink = document.getElementById('youtube-link').value;
    showLoadingBar();
    fetch('http://127.0.0.1:5000/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: youtubeLink }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('transcription-output').value = data.summary[0];
        document.getElementById('summary-output').value = data.summary[1];
        document.getElementById('transcription-output1').value = data.summary[2];
        //hideLoadingBar();
    })
    .catch(error => console.error('Error:', error));
    //hideLoadingBar();
});

document.getElementById('upload-file-button').addEventListener('click', function() {
    const fileInput = document.getElementById('upload-file');
    const file = fileInput.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        showLoadingBar();

        fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('transcription-output').value = data.summary;
            document.getElementById('summary-output').value = data.bart_summary;
            //hideLoadingBar();
        })
        .catch(error => console.error('Error:', error));
        //hideLoadingBar();
    } else {
        alert('Please select a file to upload.');
    }
});
