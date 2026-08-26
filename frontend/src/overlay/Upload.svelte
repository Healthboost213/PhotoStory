<script>

    import { uploadState } from '../store.svelte.js'

    let progressPercent = $derived(((uploadState.globalCurrentUploaded / uploadState.globalCurrentTotal) * 100).toFixed(1))
    
    $effect(() => {
        let ruler = document.getElementById("currentProgressRuler")
        console.log(ruler)
        ruler.style.width = progressPercent + "%"
    })

</script>

<div class="upload-notification">

    <div class="upload">

        <div class="empty"></div>

        <div class="progressHeader">Upload Progress - {progressPercent}%</div>

        <div class="progressBarDiv">
            <div class="progressRuler">
                <div class="currentProgressRuler" id="currentProgressRuler">

                </div>
            </div>
        </div>
        
    </div>

</div>



<style>

    * {
        box-sizing: border-box;
    }

    .upload-notification {
        position: absolute;
        top: 79%;
        left: 11.75%;
        transform: translate(-50%, -50%);
    }

    .upload {
        
        display: grid;
        grid-template-columns: 1fr;
        grid-template-rows: 0.5fr 2fr 2fr 1fr;

        width: 340px;
        height: 90px;

        background-color: var(--upload-notification-background);
        border-radius: 10px;
    }

    .progressHeader {
        text-align: center;
        padding-top: 10px;
    }

    .progressBarDiv {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .progressRuler {

        height: 7.5px;
        width: 90%;

        border-radius: 5px;
        background-color: aliceblue;
    }

    .currentProgressRuler {

        height: 7.5px;
        width: 1%;

        border-radius: 5px;
        background-color: var(--upload-bar-color);
        transition: width 400ms cubic-bezier(0.2, 0.92, 0.74, 0.96);
    }

</style>