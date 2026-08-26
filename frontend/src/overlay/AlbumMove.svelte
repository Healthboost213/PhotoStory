<script>

    import { baseUrlState } from "../store.svelte.js";

    let { closeMenu, fID, albumIDs, currentImageId } = $props()

    let derivedAlbums = $derived(albumIDs)

    async function moveImageToAlbum(event) {

        console.log(derivedAlbums)
        let albumIdToMove
        if (event.currentTarget.id === "Favourite") {
            albumIdToMove = fID
        } else {
            albumIdToMove = derivedAlbums[event.currentTarget.id]
        }

        const url = `http://${baseUrlState.currentIP}/api/albums/move`
        const message = {image_id: currentImageId, album_id: albumIdToMove}

        const request = await fetch(url, {method: "POST", body: JSON.stringify(message), credentials: "include", headers: {"Content-Type":"application/json"}})
        const response = await request.json()

        closeMenu()


    }

</script>

<div class="container">

    <div class="add-prompt">

        <h3 style="text-align: center;">Select Album</h3>

        <div class="selection-menu">

            <button id="Favourite" onclick={moveImageToAlbum} class="album-button">Favourite</button>

            {#each Object.keys(derivedAlbums) as album}
                <button id={album} onclick={moveImageToAlbum} class="album-button">{album}</button>
            {/each}

            

        </div>

        <button class="exit" onclick={closeMenu}>Exit</button>

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

        z-index: 800;
        background-color: rgba(9, 6, 6, 0.644);
    }

    .add-prompt {
        display: grid;
        width: 500px;
        height: 350px;

        padding: 40px;

        background-color: var(--popup-background);
        border: 5px solid var(--popup-border-color);
        border-radius: 10px;
    }

    .selection-menu {
        overflow-y: auto;
        scrollbar-width: none;
        border-radius: 5px;

        border: 0;
    }

    .album-button {

        display: flex;
        align-items: center;
        justify-content: center;

        width: 100%;
        height: 60px;
        background-color: var(--popup-text-background);
        color: #ffffff;
        border: 2px solid var(--primary-border-color);
        border-radius: 5px;
        margin-bottom: 5px;
    }

    .album-button:hover {
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