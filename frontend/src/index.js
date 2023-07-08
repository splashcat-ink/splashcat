// Global JS ran on every page
import "htmx.org";
import {browserInit as initHyperscript} from "hyperscript.org";

initHyperscript();

async function shareBattle(battleId) {
    if (navigator.share) {
        try {
            window.plausible('Share', {props: {type: 'Battle'}})
            await navigator.share({
                url: `https://splashcat.ink/battles/${battleId}/?share`,
            });
        } catch (err) {
            console.log(err);
        }
    }
}

const shareBattleButtons = document.querySelectorAll("button.share-battle");
for (const button of shareBattleButtons) {
    if (navigator.share) {
        button.classList.remove("hidden");
        button.addEventListener("click", () => {
            shareBattle(button.dataset.battleId)
        });
    }
}

async function shareProfile(username, cacheBuster) {
    if (navigator.share) {
        try {
            window.plausible('Share', {props: {type: 'Profile'}})
            await navigator.share({
                url: `https://splashcat.ink/@${username}/?share&cache=${cacheBuster}`,
            });
        } catch (err) {
            console.log(err);
        }
    }
}

const shareProfileButtons = document.querySelectorAll("button.share-profile");
for (const button of shareProfileButtons) {
    if (navigator.share) {
        button.classList.remove("hidden");
        button.addEventListener("click", () => {
            shareProfile(button.dataset.username, button.dataset.cacheBuster)
        });
    }
}