<script>

    import { baseUrlState } from "../store.svelte.js";

    let username = $state("")
    let password = $state("")
    let showError = $state(false)

    let { authenticateUser } = $props()

    async function loginUser() {
        
        const url = `http://${baseUrlState.currentIP}/api/authenticate`
        const details = {username: username, password: password}

        const response = await fetch(url, {method: "POST", body: JSON.stringify(details), credentials: "include", headers: {"Content-Type":"application/json"}})
        const result = await response.json()

        if (result.status === "authenticated") {
            authenticateUser()
        }

    }

</script>

<div class="container">

    <div class="login">

        <h3 style="text-align: center;">Welcome Back To PhotoStory</h3>

        <label for="username" class="field-labels">Username </label>
        <input type="text" name="username" id="username" class="input-fields" bind:value={username} placeholder="Enter your username" required>
        <label for="password" class="field-labels">Password </label>
        <input type="password" name="password" id="password" class="input-fields" bind:value={password} placeholder="Enter your password" required>

        <button class="submit" onclick={loginUser}>Login</button>

        {#if showError}
            <h5 style="font-size: 14px">Incorrect Username or Password</h5>
        {/if}

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

    .login {
        display: grid;
        width: 100%;
        max-width: 500px;

        padding: 50px;

        background-color: var(--popup-background);
        border: 5px solid var(--popup-border-color);
        border-radius: 10px;
    }

    .field-labels {
        display: inline-block;
        font-size: 15px;
        margin-top: 10px;
    }

    .input-fields {
        display: block;
        height: 40px;
        width: 100%;

        padding-left: 10px;
        background-color: var(--popup-text-background);
        border: 2px solid var(--primary-border-color);
        color: #ffffff;

        border-radius: 5px;
        margin-top: 5px
    }

    .input-fields::placeholder {
        font-family: 'Lexend';
        font-weight: 600;
    }

    .submit {

        display: inline-block;
        margin-top: 30px;
        width: 100%;
        height: 35px;
        padding: 5px;
        
        align-self: center;
        justify-self: center;

        border-radius: 7.5px;
        border-width: 0px;

        background-color: var(--upload-button-background);
        color: white;
    }

    .submit:active {
        background-color: var(--upload-button-hover);
    }

</style>