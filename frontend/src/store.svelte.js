export let uploadState = $state({
    isUploading: false,
    globalCurrentUploaded: 0,
    globalCurrentTotal: 0
})

export const baseUrlState = $state({
    currentIP: "",
})