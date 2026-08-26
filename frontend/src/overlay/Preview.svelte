<script>

    import fileIcon from '../assets/icons/file-image.svg'
    import hashIcon from '../assets/icons/hashtag.svg'
    import resoIcon from '../assets/icons/ruler-combined.svg'
    import calendarIcon from '../assets/icons/calendar.svg'
    import closeIcon from '../assets/icons/xmark.svg'

    import linkIcon from '../assets/icons/arrow-up-right-from-square.svg'
    import folderTreeIcon from '../assets/icons/folder-tree.svg'
    import binIcon from '../assets/icons/trash-can.svg'

    import { baseUrlState } from "../store.svelte.js";

    let { isPreview = $bindable(), currentImageId, refreshGrid, openAlbumMove } = $props()
    let imageData = $state({})

    function closePreview () {
        isPreview = false
    }

    async function getImageDetails () {
        const url = `http://${baseUrlState.currentIP}/api/image/info/${currentImageId}`
        const request = await fetch(url, {method: "GET", credentials: "include"})
        const response = await request.json()

        imageData = response
    }

    function openImageInNewTab() {
        const url = `http://${baseUrlState.currentIP}/api/image/download/${currentImageId}`
        window.open(url, '_blank')
    }

    async function deleteImage() {
        
        const url = `http://${baseUrlState.currentIP}/api/delete/${currentImageId}`
        const response = await fetch(url, {method: "POST", credentials: "include"})
        const result = await response.json()
        console.log(result)
        closePreview()
        refreshGrid()

    }

    $effect(() => getImageDetails())

</script>

<div class="container">

    <div class="image-preview">

        <img src="http://{baseUrlState.currentIP}/api/image/download/{currentImageId}" class="image-style" alt="">

    </div>

    <div class="image-menu">

        <div class="image-details">

            <div class="header-div">
                <h3 class="header-text">Image Details</h3>
                <button class="close-button" onclick={closePreview}>
                    <img src={closeIcon} alt="">
                </button>
            </div>

            <div class="info-div">
                <div class="field-icon">
                    <img src={fileIcon} alt="">
                </div>
                <div class="info-sub-div">
                    <h5 class="section-header">Image Name</h5>
                    <h5 class="section-info-text">{imageData.ImageName}</h5>
                </div>
            </div>
            <div class="info-div">
                <div class="field-icon">
                    <img src={hashIcon} alt="">
                </div>
                <div class="info-sub-div">
                    <h5 class="section-header">Image ID</h5>
                    <h5 class="section-info-text">{imageData.ImageId}</h5>
                </div>
            </div>
            <div class="info-div">
                <div class="field-icon">
                    <img src={resoIcon} alt="">
                </div>
                <div class="info-sub-div">
                    <h5 class="section-header">Image Resolution</h5>
                    <h5 class="section-info-text">{imageData.ImageXRes}px x {imageData.ImageYRes}px</h5>
                </div>
            </div>
            <div class="info-div">
                <div class="field-icon">
                    <img src={calendarIcon} alt="">
                </div>
                <div class="info-sub-div">
                    <h5 class="section-header">Date Taken</h5>
                    <h5 class="section-info-text">{imageData.ImageDateTaken}</h5>
                </div>
            </div>

        </div>

        <div class="image-actions">

            <div><button onclick={openImageInNewTab}><img src={linkIcon} alt="" class="action-icon">Open In New Tab</button></div>
            <div><button onclick={openAlbumMove}><img src={folderTreeIcon} alt="" class="action-icon">Add To Album</button></div>
            <div><button class="delete-button" onclick={deleteImage}><img src={binIcon} alt="" class="action-icon">Delete Image</button></div>

        </div>

    </div>

</div>

<style>

    /* image-preview > container > image-preview */

    * {
        box-sizing: border-box;
    }

    .container {

        min-height: 0;
        min-width: 0;
        width: 100vw;

        display: flex;
        gap: 5px;

        z-index: 200;
        background-color: var(--image-preview-background);
    }

    /* Image Display */

    .image-preview {
        
        flex: 2;
        min-height: 0;

        display: block;
        justify-content: center;
        align-items: center;

        margin: 20px;

    }

    .image-style {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    /* Image Menu */

    .image-menu {
        flex: 1;

        min-width: 0;
        display: flex;
        flex-direction: column;

        margin: 20px 20px 20px 0px;
        
        background-color: var(--image-details-background);
        color: white;
        border-radius: 10px;
    }

    /* Image Details Sub-Menu */

    .image-details {
        flex: 4;

        display: flex;
        flex-direction: column;
        gap: 0px;

        height: 100%;
        margin: 10px;
        border: 2px solid var(--preview-border-color);
        border-radius: 5px;

        background-color: var(--image-div-background);
    }

    .image-details > .header-div {
        
        flex: 1;
        display: flex;
        align-items: center;
       
    }

    .header-text {
        margin-left: 20px;
    }

    .close-button {
        width: 40px;
        height: 40px;

        margin-left: auto;
        margin-right: 20px;
        border: 2px solid var(--preview-border-color);
        border-radius: 5px;

        background-color: var(--image-icon-background);
    }

    .close-button:active {
        background-color: #111623;
    }

    .close-button > img {
        display: block;
    }

    .close-button:hover {
        cursor: pointer;
    }

    .info-div {
        
        flex: 1;

        min-width: 0;

        display: flex;
        align-items: center;

        border-top: 2px solid var(--preview-border-color);
        margin: 0px 10px 0px 10px;
    }

    .info-sub-div {

        min-width: 0;

        display: flex;
        flex-direction: column;
        gap: 0px;

        margin-left: 30px;
    }

    .section-header {
        font-size: 13px;
        font-weight: 500;
        margin: 0px 0px 10px 0px;
    }

    .section-info-text {
        margin: 0;
        word-break: break-all;
        text-wrap-style: pretty;
        padding-right: 20px;
    }

    .field-icon {

        flex-shrink: 0;
        width: 40px;
        height: 40px;

        margin-left: 10px;
        padding: 7.5px;
        border-radius: 5px;

        background-color: var(--image-icon-background);

    }

    /* Image Actions Sub-Menu */


    .image-actions {
        flex: 1;

        display: flex;
        flex-direction: column;
        gap: 5px;

        margin: 10px;
        margin-top: 0px;
        border-radius: 5px;    

    }

    .image-actions > div {
        
        flex: 2;
        border-radius: 5px;

    }

    .image-actions > div > button {
        
        width: 100%;
        height: 100%;

        display: flex;
        align-items: center;

        border: 2px solid var(--preview-border-color);
        border-radius: 5px;

        text-align: left;
        color: white;
        background-color: var(--image-div-background);
        
    }

    .image-actions > div > button:hover {
        transition: 0.3s;
        background-color: #0d111d;
        cursor: pointer;
    }

    .delete-button {

        border: 2px solid #3a2121 !important;
        background-color: #161725 !important;
        color: #BD393D !important;
        
    }

    .delete-button:hover {

        transition: 0.3s;
        background-color: #11121c !important;
        color: #BD393D rgb(38, 41, 71);
        
    }

    .action-icon {
        height: 20px;
        margin-left: 5px;
        margin-right: 10px;
    }

</style>