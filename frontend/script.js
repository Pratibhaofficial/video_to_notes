async function uploadFile() {
   const file = document.getElementById("fileInput").files[0];

   const formData = new FormData();
   formData.append("file", file);

   const res = await fetch("http://127.0.0.1:8000/upload", {
       method: "POST",
       body: formData
   });

   const data = await res.json();

    console.log(data);  // 🔥 see actual response

    if (data.transcript) {
        document.getElementById("transcript").innerText = data.transcript;
    } else {
        document.getElementById("transcript").innerText = "Error loading transcript";
    }

    if (data.notes) {
        document.getElementById("notes").innerText = data.notes;
    }
}


async function askQuestion() {
   const query = document.getElementById("query").value;

   const res = await fetch(`http://127.0.0.1:8000/ask?query=${query}`, {
       method: "POST"
   });

   const data = await res.json();

   document.getElementById("answer").innerText = data.answer;
}