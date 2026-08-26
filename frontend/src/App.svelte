<script>

    import Menu from './body/Menu.svelte'
    import AlbumPane from './body/AlbumPane.svelte'
    import Grid from './body/Grid.svelte'

    import Login from './overlay/Login.svelte'
    import Loading from './overlay/Loading.svelte'
    import Upload from './overlay/Upload.svelte'

    import { uploadState, baseUrlState } from './store.svelte.js'


    // Authentication States
    let isAuthenticated = $state(false)
    let isChecking = $state(true)
    let currentUsername = $state("")

    // Redraw States (Change to Callbacks)
    let uploadRedraw = $state(0)
    let albumAddRedraw = $state(0)

    // Authentication Code

    async function startAuthenticate () {
        
        const url = `http://${baseUrlState.currentIP}/api/user`
        const response = await fetch(url, {method: "POST", credentials: "include"})
        const result = await response.json()
        
        if (result.status === "authenticated") {
            isAuthenticated = true
            isChecking = false
            currentUsername = result.username
        } else {
            isChecking = false
        }

    }

    function loginAuthenticate() {
        isAuthenticated = true
        window.location.reload()
    }

    // Album Selection Code

    let currentAlbum = $state("All")
    let albumObject = $state({})
    let allID = $state()
    let favouriteID = $state()

    async function initialiseAlbumList () {

        const url = `http://${baseUrlState.currentIP}/api/albums/list`
        const request = await fetch(url, {method: "GET", credentials: "include"})
        const response = await request.json()
                
        if (response.All !== undefined) {
            allID = response.All 
            favouriteID = response.Favourite

            let { All, Favourite, ...finalAlbumList } = response
            albumObject = finalAlbumList
        }

    }

    function changeAlbum(albumName) {
        currentAlbum = albumName
    }
    
    $effect(() => {

        baseUrlState.currentIP = localStorage.getItem("SavedIP")
        startAuthenticate()
        
        if (isAuthenticated) {
            initialiseAlbumList()
        }
    })

</script>


<div class="app">

    <div class="album-panel">

        <AlbumPane {currentAlbum} changeCurrentAlbum={changeAlbum} {currentUsername} {albumObject} initAlbums={initialiseAlbumList}/>

    </div>

    <div class="main-grid">

        <Menu bind:uploadRedraw {currentAlbum} />

        {#key [currentAlbum, uploadRedraw]}
            <Grid {currentAlbum} {albumObject} {allID} {favouriteID} />
        {/key}

    </div>

    {#if uploadState.isUploading}
        <Upload />
    {/if}

</div>

{#if !isAuthenticated && !isChecking}

    <div class="login-panel">
        <Login authenticateUser={loginAuthenticate} />
    </div>
    
{/if}

{#if isChecking}

    <div class="loading-overlay">
        <Loading authConnection={startAuthenticate}/>
    </div>
    
{/if}

<style>

    .app {

        height: 100vh;
        width: 100vw; 
        display: flex;
        flex-direction: row;

    }

    .album-panel {

        display: flex;
        flex-direction: column;
        flex: 1.25;

        border-right: 1px var(--primary-border-color) solid;
        background-color: var(--album-panel-background);

    }

    .main-grid {
        display: flex;
        flex-direction: column;
        flex: 4;
        background-color: var(--main-grid-background);
        min-width: 0;
    }

    .login-panel {
        position: absolute;
        top: 0;
        left: 0;
    }

    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
    }

</style>