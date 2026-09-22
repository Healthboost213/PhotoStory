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
    let photos = $state({})

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
            const url = `${baseUrlState.currentIP}/api/thumbnail/${targetAlbumId}/${photoOffset}`
            const response = await fetch(url, {method: "POST", credentials: "include"})
            const result = await response.json()

            if (result.hasMore) {
                for (const [k, v] of Object.entries(result.imageHashes)) {
                    if (!photos[v.DateTaken]) {
                        photos[v.DateTaken] = []
                        photos[v.DateTaken].push(v.ImageId)
                    } else {
                        photos[v.DateTaken].push(v.ImageId)
                    }   
                }
                photoOffset += 50
                hasMoreToLoad = true
            } else {
                hasMoreToLoad = false
                throbberText.innerText = "This Is The End."
            } 
        }
    }

    function updateDeleteRefreshState() {
        photoOffset = 0
        photos = {}
        getPhotosList() 
    }

    function formatDate(dateString) {
        
        let dateObj = new Date(dateString)
        let baseStr = ""

        let month = dateObj.getMonth()
        switch (month) {
            case 0: baseStr = "January "
                break
            case 1: baseStr = "February "
                break
            case 2: baseStr = "March "
                break
            case 3: baseStr = "April "
                break
            case 4: baseStr = "May "
                break
            case 5: baseStr = "June "
                break
            case 6: baseStr = "July "
                break
            case 7: baseStr = "August "
                break
            case 8: baseStr = "September "
                break
            case 9: baseStr = "October "
                break
            case 10: baseStr = "November "
                break
            case 11: baseStr = "December "
                break
        }

        let date = dateObj.getDate()
        switch (date) {
            case 1: baseStr += String(date) + "st"
                break;
            case 2: baseStr += String(date) + "nd"
                break;
            case 3: baseStr += String(date) + "rd"
                break;
            default: baseStr += String(date) + "th"
                break;
        }

        baseStr = baseStr + " " + dateObj.getFullYear()

        return baseStr

    }

    $effect(() => {

        if (targetAlbumId && sentinel) {
            const callback = (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting === true && hasMoreToLoad === true) {
                        getPhotosList()
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

    {#each Object.entries(photos) as [date, array]}
            
        <h4 class="date-text">{formatDate(date)}</h4>

        {#each array as photoHash}
            <div class="image-area">
                <img src="{baseUrlState.currentIP}/api/thumbnail/download/{photoHash}" onclick={openImagePreview} id={photoHash} alt="" class="image-style">
            </div>
        {/each}

    {/each}
        
    <div id="sentinel" class="sentinel" bind:this={sentinel}>
        <h4 id="throbber-text" class="throbber-text" bind:this={throbberText}>This Is The End.</h4>
    </div>

    <div class="preview-overlay">

        {#if isPreview}
            <Preview bind:isPreview {currentImageId} refreshGrid={updateDeleteRefreshState} openAlbumMove={openAlbumMove} {currentAlbum} {albumObject} {favouriteID}/>
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
        align-content: start;
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
        aspect-ratio: 1/1;
        border-radius: 5%;
                
        background-color: var(--image-area-background);

    }

    .image-style {

        display: block;
        width: 100%;
        height: 100%;
        border-radius: 5%;
        transition: 0.2s; 
        object-fit: cover;
    
    }

    .image-style:hover {
        cursor: pointer;
        transform: scale(1.035);
        transition: 0.2s;
    }

    .date-text {

        display: flex;
        justify-content: start;
        align-items: center;

        max-height: 10px;
        padding-top: 30px;
        grid-column: 1 / 6;
        padding-left: 10px;

        font-size: 20px;
    }

    .date-text:first-child {
        padding-top: 0px;
    }

    .sentinel {

        display: flex;
        justify-content: center;
        align-items: center;

        height: 90px;
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