<script>

    import { onMount } from "svelte"
    import { baseUrlState } from "../store.svelte.js"

    import Preview from '../overlay/Preview.svelte'
    import AlbumMove from '../overlay/AlbumMove.svelte'

    let { currentAlbum , albumObject, allID, favouriteID } = $props()

    let isPreview = $state(false)
    let currentImageId = $state("")

    let isMove = $state(false)
    
    let photoOffset = $state(0)
    let hasMoreToLoad = $state(true)
    const photos = $state([])

    let deleteRefresh = $state(0)

    let sentinel, throbberText = $state()

    let targetAlbumId = $derived.by(() => {
        if (currentAlbum === "All") return allID
        if (currentAlbum === "Favourite") return favouriteID
        return albumObject[currentAlbum]
    })

    function openImagePreview (element) {
        currentImageId = element.target.id
        isPreview = true
    }

    function openAlbumMove () {
        isMove = true
    }

    function closeAlbumMove () {
        isMove = false
    }

    async function getPhotosList () {
        
        if (targetAlbumId) {
            const url = `http://${baseUrlState.currentIP}/api/thumbnail/${targetAlbumId}/${photoOffset}`
            const response = await fetch(url, {method: "POST", credentials: "include"})
            const result = await response.json()

            if (result.hasMore) {
                for (const [k, v] of Object.entries(result.imageHashes)) {
                    photos.push(v.ImageId)
                }
                hasMoreToLoad = true
            } else {
                hasMoreToLoad = false
                throbberText.innerText = "This Is The End."
            }

            
        }
    }

    function updateDeleteRefreshState() {
        photoOffset = 0
        photos.length = 0
        getPhotosList()
    }

    $effect(() => {

        if (targetAlbumId && sentinel) {
            const callback = (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting === true && hasMoreToLoad === true) {
                        getPhotosList()
                        photoOffset += 50
                    }
                })
            }

            const options = {
                root: document.querySelector("#grid-area"),
                rootMargin: "0px",
                scrollMargin: "800px",
                threshold: 0.0
            }

            const observer = new IntersectionObserver(callback, options)
            observer.observe(sentinel)
        }

    })

</script>


    
<div class="grid-area">

    {#each photos as photoHash}
            
        <div class="image-area">
            <img src="http://{baseUrlState.currentIP}/api/thumbnail/download/{photoHash}" onclick={openImagePreview} id={photoHash} alt="" class="image-style">
        </div>

    {/each}
        
    <div id="sentinel" class="sentinel" bind:this={sentinel}>
        <h4 id="throbber-text" class="throbber-text" bind:this={throbberText}>This Is The End.</h4>
    </div>

    <div class="preview-overlay">

        {#if isPreview}
            <Preview bind:isPreview {currentImageId} refreshGrid={updateDeleteRefreshState} openAlbumMove={openAlbumMove}/>
        {/if}
            
    </div>
    
    <div class="move-overlay">

        {#if isMove}
            <AlbumMove closeMenu={closeAlbumMove} fID={favouriteID} albumIDs={albumObject} {currentImageId} />
        {/if}

    </div>
        
</div>

<style>

    .grid-area {

        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
        gap: 10px;

        flex: 1;
        min-height: 0;
        overflow-y: auto;
        min-width: 0;
        scrollbar-width: none;

        padding: 10px;
    }

    .image-area {

        min-width: 0;
        width: 100%;
        border-radius: 5%;
        aspect-ratio: 1 / 1;

        background-color: var(--image-area-background);

    }

    .image-style {

        display: block;
        width: 100%;
        height: 100%;
        border-radius: 5%;
        transition: 0.2s

    }

    .image-style:hover {
        cursor: pointer;
        transform: scale(1.05);
        transition: 0.2s;
    }

    .sentinel {

        display: flex;
        justify-content: center;
        align-items: center;

        height: 60px;
        grid-column: 1 / 6;
    }

    .throbber-text {
        color: #c1c0c04d;
    }

    .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;

        display: flex;
        overflow-y: hidden;
        height: 100vh;
    }

    .move-overlay {
        position: absolute;
        top: 0;
        left: 0;

        display: flex;
        overflow-y: hidden;
        height: 100vh;
    }

</style>