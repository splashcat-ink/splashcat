// Global JS ran on every page
import * as htmx from "htmx.org";
import {browserInit as initHyperscript} from "hyperscript.org";

initHyperscript();
window.htmx = htmx;

async function webShare(url) {
    if (navigator.share) {
        try {
            await navigator.share({
                url,
            });
        } catch (err) {
            console.log(err);
        }
    }
}

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (err) {
        console.error(err.name, err.message);
    }
}

const shareButtons = document.querySelectorAll("button.share-button");
for (const button of shareButtons) {
    if (button.dataset.shareType === "webShare") {
        if (!navigator.share) {
            button.style.display = "none";
        }
        button.addEventListener("click", (event) => {
            event.preventDefault();
            window.plausible('Share', {props: {type: button.dataset.contentType, shareType: button.dataset.shareType}});
            webShare(button.dataset.url);
        });
    } else if (button.dataset.shareType === "clipboard") {
        button.addEventListener("click", async (event) => {
            event.preventDefault();
            window.plausible('Share', {props: {type: button.dataset.contentType, shareType: button.dataset.shareType}});
            await copyToClipboard(button.dataset.url);
            button.classList.add("copy-tooltipped");
        });
        button.addEventListener("mouseleave", () => button.classList.remove("copy-tooltipped"));
        button.addEventListener("blur", () => button.classList.remove("copy-tooltipped"));
    }
}