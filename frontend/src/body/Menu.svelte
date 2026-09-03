<script>

    import { uploadState, baseUrlState } from "../store.svelte.js";

    let { uploadRedraw = $bindable(), currentAlbum } = $props()

    function clickFunction() {
        const uploadButton = document.getElementById("secretUploadButton")
        uploadButton.click()
    }

    function changeUploadRefreshState() {
        uploadRedraw++
    }

    async function fileUpload() {

        const fileList = Array.from(document.getElementById("secretUploadButton").files)
        const url = `http://${baseUrlState.currentIP}/api/upload`

        uploadState.globalCurrentTotal = fileList.length
        

        if (uploadState.globalCurrentTotal > 0) {

            uploadState.isUploading = true
            
            let start = performance.now()

            for (let i = 0; i< fileList.length; i+=5) {

                const batchList = fileList.slice(i, i+5)
                
                const promiseList = batchList.map((file) => {
                    const form = new FormData()
                    form.append('file_upload', file)
                    uploadState.globalCurrentUploaded += 1
                    return fetch(url, {method: "POST", credentials: "include", body: form})
                })

                await Promise.allSettled(promiseList)
                
            }

            console.log(performance.now() - start)

            uploadState.isUploading = false
            uploadState.globalCurrentUploaded = 0
            uploadState.globalCurrentTotal = 0
            document.getElementById("secretUploadButton").value = ""

        } else (
            alert("You can't upload with no files")
        )

        changeUploadRefreshState()

    }

</script>

<div class="menu">

    <h1 class="header-text">{currentAlbum}</h1>

    <input type="file" name="" class="secret-upload-button" id="secretUploadButton" multiple>

    <button onclick={clickFunction} class="select-button">Select Images</button>
    <button onclick={fileUpload} class="upload-button">Upload</button>

</div>

<style>

    .menu {

        display: flex;
        flex-direction: row;
        align-items: center;

        height: 120px;

    }

    .header-text {
        margin-left: 30px;

        font-family: 'Lexend';
        font-weight: 800;
        letter-spacing: 1px;
    }

    /* Button Designs */

    .secret-upload-button {
        display: none;
    }

    .select-button {
        
        height: 40px;
        width: 120px;

        border: none;
        border-radius: 5px;

        background-color: var(--upload-button-background);
        color: #ffffff;

        margin-left: auto;
        margin-right: 10px;
        padding: 10px;
        transition: 200ms;

    }

    .select-button:hover {
        
        cursor: pointer;
        background-color: var(--upload-button-hover);
        transition: 200ms;
        
    }

    .upload-button {
        
        height: 40px;
        width: 120px;

        border: none;
        border-radius: 5px;

        background-color: var(--upload-button-background);
        color: #ffffff;

        margin-right: 20px;
        padding: 10px;
    
    }

    .upload-button:hover {
        
        cursor: pointer;
        background-color: var(--upload-button-hover);
        transition: 200ms;

    }

</style>

