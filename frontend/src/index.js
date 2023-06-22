// Global JS ran on every page
import "htmx.org";
import {browserInit as initHyperscript} from "hyperscript.org";

initHyperscript();

async function shareBattle(battleId) {
    if (navigator.share) {
        try {
            window.plausible('Share', {props: {type: 'Battle'}})
            await navigator.share({
                url: `https://splashcat.ink/battle/${battleId}/?share`,
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