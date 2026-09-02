<script>

    import AlbumAdd from "../overlay/AlbumAdd.svelte"

    import { baseUrlState } from "../store.svelte.js"

    import logOutIcon from "../assets/icons/arrow-right-from-bracket.svg"
    import userAccountIcon from "../assets/icons/circle-user.svg"
    import trashIcon from "../assets/icons/trash-can-white.svg"

    let { currentAlbum , changeCurrentAlbum, currentUsername, albumObject, initAlbums } = $props()


    let albumAddMenuOpen = $state(false)
    let albumRefresh = $state(0)

    let previousAlbum = $state()

    function toggleSelectedAlbum (event) {
        changeCurrentAlbum(event.currentTarget.id)
    }

    async function logOutUser() {
        const url = `http://${baseUrlState.currentIP}/api/logout`
        const response = await fetch(url, {method: "POST", credentials: "include"})
        const result = await response.json()
        window.location.reload()
    }

    async function deleteAlbum() {

        if (currentAlbum === "All") return
        if (currentAlbum === "Favourite") return
        
        const url = `http://${baseUrlState.currentIP}/api/albums/delete`
        const message = {album_id: albumObject[currentAlbum]}

        const request = await fetch(url, {method: "POST", body: JSON.stringify(message), credentials: "include", headers: {"Content-Type":"application/json"}})
        const response = await request.json()
        
        if (response.status === "success") {
            changeCurrentAlbum("All")
            initAlbums()
        }
        
        
    }

    // Add Album Menu

    function openAlbumAddMenu() {
        albumAddMenuOpen = true
    }

    function closeAlbumAddMenu() {
        albumAddMenuOpen = false
        initAlbums()
    }
    
    let derivedAlbumObject = $derived(albumObject)

</script>

<div class="logo-section">

</div>

{#key albumRefresh}

<div class="album-section">

    <div class="header-div">

        <h5 class="header-text">Library</h5>

        {#if (currentAlbum !== "All") && (currentAlbum !== "Favourite")}
            <button class="delete-album-div" onclick={deleteAlbum}>
                <img class="delete-icon" src={trashIcon} alt="">
            </button>
        {/if}

    </div>

    <div class="album-list">
        
        <button id="All" class={currentAlbum === "All" ? "selected-album" : null} onclick={toggleSelectedAlbum}>
            <h4>All</h4>
        </button>

        <button id="Favourite" class={currentAlbum === "Favourite" ? "selected-album" : null} onclick={toggleSelectedAlbum}>
            <h4>Favourite</h4>
        </button>

        {#each Object.keys(derivedAlbumObject) as albumNames}
            
            <button id={albumNames} class={currentAlbum === albumNames ? "selected-album" : null} onclick={toggleSelectedAlbum}>
                <h4>{albumNames}</h4>
            </button>

        {/each}

        <button onclick={openAlbumAddMenu}><h4>+ Add Album</h4></button>

    </div>

</div>

{/key}

<hr class="divider">

<div class="profile-section">

    <img src={userAccountIcon} class="profile-image" alt="profile" width="60">

    <h4 class="profile-username">{currentUsername}</h4>

    <button onclick={logOutUser} class="logout-button">
        <img src={logOutIcon} alt="">
    </button>

</div>

{#if albumAddMenuOpen}
    <div class="album-add">
        <AlbumAdd closeMenu={closeAlbumAddMenu} />
    </div>
{/if}


<style>

    /* div styling */

    .logo-section {
        height: 120px;
        background-color: var(--logo-section-background);
    }

    .album-section {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-height: 0;
    }

    .profile-section {
        display: flex;
        height: 80px;
        justify-self: center;
        width: 90%;
        margin: 0 0 10px 5%;
        border-radius: 5px;
        background-color: var(--upload-notification-background);

        align-items: center;
    }

    .divider {
        border: none;
        height: 2px;
        width: 90%; 
        
        background-color: var(--primary-border-color);
    }

    /* header */

    .header-div {
        display: flex;
        align-items: center;
    }

    .header-text {
        color: #ffffff;
        margin-left: 20px;
        font-size: 15px;
    }

    /* album list navigation */

    .album-list {
        min-height: 0;
        overflow-y: scroll;
        scrollbar-width: none;
    }

    .album-list > button {
        background-color: var(--album-panel-background);
        display: flex;

        width: 90%;
        height: 50px;
        padding: 5px;
        margin: 0px 10px 10px 15px;

        border: 2px var(--primary-border-color) solid;
        border-radius: 5px;
    }

    .album-list > .selected-album {
        
        display: flex;

        width: 90%;
        height: 50px;
        
        padding: 5px;
        margin: 0px 10px 10px 15px;
        border: 2px #1e5590 solid;
        border-radius: 5px;

        background-color: #111F40;

    }

    .album-list > .selected-album > h4 {
        
        color: #2F86E4;

    }

    .album-list > button:hover {
        transform: scale(1.015);
        transition: 0.1s;
        cursor: pointer;
    }

    .album-list > button > h4 {
       
        align-self: center;
        padding-left: 15px;
        
        color: white;
        font-size: 14px;

    }

    .delete-album-div {
        
        align-self: center;

        height: 35px;
        width: 35px;
        
        margin-left: auto;
        margin-right: 20px;
        border: 2px solid white;
        border-radius: 3px;
        
        background-color: var(--logout-button-color);
        transition: 0.2s;
    }

    .delete-album-div:hover {
        
        transition: 0.2s;
        background-color: var(--logout-button-color-hover);

    }

    .delete-icon {
        height: 100%;
        width: 100%;
    }

    /* Profile Section */

    .profile-image {
        width: 50px;
        height: 50px;

        border-radius: 40px;
        margin-left: 20px;
    }

    .profile-username {
        margin-left: 20px;
    }

    .logout-button {
        
        height: 40px;
        width: 40px;

        border: none;
        border-radius: 5px;

        background-color: var(--logout-button-color);
        color: #ffffff;

        margin-left: auto ;
        margin-right: 20px;
        padding: 10px;
        transition: 0.3s
    }

    .logout-button > img {
        max-height: 80%;
        fill: white;
    }

    .logout-button:hover {
        
        transition: 0.3s;
        background-color: var(--logout-button-color-hover);
        cursor: pointer;

    }

    .album-add {
        position: absolute;
        top: 0;
        left: 0;
    }

</style>