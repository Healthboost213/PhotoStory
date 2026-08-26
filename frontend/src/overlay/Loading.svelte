<script>

    import { baseUrlState } from "../store.svelte.js";

    let { authConnection } = $props()

    function enterIpAddress () {
        
        let ipAddressEntered = prompt("Enter IP Address of the Endpoint (e.g. 127.0.0.1:5000)")
        let ipAddressRegex = null
        let localhostRegex = new RegExp("localhost:\\d{1,5}")

        localStorage.setItem("SavedIP", ipAddressEntered)
        window.location.reload()
    
    }

</script>

<div class="container">

    <div class="loading">

        <h3 style="text-align: center;">Loading...</h3>

        <button class="ip-button" onclick={enterIpAddress}>Change IP?</button>

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

    .loading {
        display: grid;
        width: 100%;
        max-width: 500px;

        padding: 50px;

        place-items: center;

        background-color: var(--popup-background);
        border: 5px solid var(--popup-border-color);
        border-radius: 10px;
    }

    .ip-button {
        width: 100px;
        padding: 10px;
        background-color: var(--cancel-button-background);
        color: white;
        border: 0 red solid;
        border-radius: 5px;
    }

    .ip-button:active {
        background-color: var(--cancel-button-hover);
    }

    .ip-button:hover {
        cursor: pointer;
    }

</style>