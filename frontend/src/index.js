// Global JS ran on every page
import * as htmx from "htmx.org";
import "./htmx-ext/loading-states.js";
import {browserInit as initHyperscript} from "hyperscript.org";
import Idiomorph from "idiomorph";

initHyperscript();
window.htmx = htmx;

// copied from idiomorph/dist/idiomorh-ext.js
htmx.defineExtension('morph', {
	isInlineSwap: function (swapStyle) {
		return swapStyle === 'morph';
	},
	handleSwap: function (swapStyle, target, fragment) {
		if (swapStyle === 'morph' || swapStyle === 'morph:outerHTML') {
			return Idiomorph.morph(target, fragment.children);
		} else if (swapStyle === 'morph:innerHTML') {
			return Idiomorph.morph(target, fragment.children, {morphStyle: 'innerHTML'});
		}
	}
});


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
	initShareButton(button)
}

function initShareButton(button) {
	if (button.dataset.initShare) return;
	button.dataset.initShare = 'true';
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

window.initShareButton = initShareButton;

window.addEventListener(
	"message",
	(event) => {
		if (event.data[0] === "resize") {
			console.log(event)
			console.log("resizing", event.data[1])
			document.querySelector("iframe").style.height = event.data[1] + "px";
		}
	},
);

document.querySelectorAll(".battle-pagination-button").forEach(button => button.addEventListener("click", event => {
	const direction = event.target.dataset.direction ?? "unknown";

	sessionStorage.setItem("direction", direction);
	console.log("wrote direction", direction)
}))

window.addEventListener("pageswap", e => {
	if (e.viewTransition) {
		console.log("swap", e.viewTransition, sessionStorage.getItem("direction"))
		e.viewTransition.types.add(sessionStorage.getItem("direction"));
	}
})