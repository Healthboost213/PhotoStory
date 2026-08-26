<script>

    import { baseUrlState } from "../store.svelte.js";

    let { closeMenu } = $props()

    let fieldInput = $state()

    async function createNewAlbum(albumName) {
        
        const url = `http://${baseUrlState.currentIP}/api/albums/create`
        const details = {album_name: albumName}
        
        if (details.album_name) {
            const request = await fetch(url, {method: "POST", body: JSON.stringify(details), credentials: "include", headers: {"Content-Type":"application/json"}})
            const response = await request.json()
            closeMenu()
        }
    }

</script>

<div class="container">

    <div class="add-prompt">

        <h3 style="text-align: center;">Create New Album</h3>

        <div class="form-control">
            <input type="text" name="albumName" id="albumName" class="input-fields" bind:value={fieldInput} placeholder="Enter Album Name...">
            <button class="submit" onclick={() => {createNewAlbum(fieldInput)}}>Submit</button>
        </div>
        
        <button class="exit" onclick={closeMenu}>Close</button>

    </div>

</div>


<style>

    * {
        box-sizing: border-box;
    }

    .container {
        display: grid;
        min-height: 100vh;
        min-width: 100vw;
        place-items: center;  

        z-index: 200;
        background-color: rgba(9, 6, 6, 0.644);
    }

    .add-prompt {
        display: grid;
        width: 100%;
        max-width: 500px;

        padding: 50px;
        border: 5px solid var(--popup-border-color);
        background-color: var(--popup-background);
        border-radius: 10px;
    }

    .form-control {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .input-fields {
        flex: 3;
        height: 40px;
        width: 100%;
        padding-left: 10px;
        background-color: var(--popup-text-background);
        border: 2px solid var(--primary-border-color);
        color: white;
        border-radius: 5px;
    }

    .input-fields::placeholder {
        font-family: 'Lexend';
        font-weight: 600;
    }

    .submit {

        flex: 0.5;

        display: inline-block;
        width: 100%;
        height: 40px;
        
        align-self: center;
        justify-self: center;

        border-radius: 5px;
        border-width: 0px;

        background-color: var(--upload-button-background);
        color: white;
    }

    .submit:active {
        background-color: var(--upload-button-hover);
    }

    .submit:hover {
        cursor: pointer;
    }

    .exit {

        display: inline-block;
        margin-top: 30px;
        width: 100%;
        height: 35px;
        padding: 5px;
        
        align-self: center;
        justify-self: center;

        border-radius: 5px;
        border-width: 0px;

        background-color: var(--cancel-button-background);
        color: white;
    }

    .exit:active {
        background-color: var(--cancel-button-hover);
    }

    .exit:hover {
        cursor: pointer;
    }


</style>