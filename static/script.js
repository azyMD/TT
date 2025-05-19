function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  const language = document.getElementById('language').value;
  const file = fileInput.files[0];

  if (!file) {
    alert('Please select a file.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  fetch('/transcribe', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('original').innerText = data.original;
      document.getElementById('review').innerText = data.review;
    })
    .catch(err => {
      alert("Error uploading file: " + err);
    });
}
