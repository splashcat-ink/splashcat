#!/usr/bin/env node
import {fileURLToPath} from "url";
import {readFile, writeFile} from "fs/promises";
import {join} from "path";
import {watch} from "chokidar";
import {debounce} from "tiny-throttle";
import {build, context} from "esbuild";
import postcss from "postcss";
import tailwind from "tailwindcss";
import cssnano from "cssnano";
import autoprefixer from "autoprefixer";

const dirname = fileURLToPath(new URL('.', import.meta.url));

/** @type {import("esbuild").BuildOptions} */
let esbuildOptions = {
    entryPoints: [
        join(dirname, "src", "index.js")
    ],
    bundle: true,
    sourcemap: true,
    outdir: join(dirname, "..", "static", "js"),
    minify: true
};

/** @type {import("postcss").ProcessOptions} */
let postcssOptions = {
    from: join(dirname, "src", "styles.css"),
    to: join(dirname, "..", "static", "css", "styles.css"),
    map: {
        inline: false
    },
}

const cssProcessor = postcss([
    tailwind(join(dirname, "tailwind.config.js")),
    autoprefixer(),
    cssnano()
]);

// HACK: for some reason this terribleness has to be done to make PostCSS not hang trying to read every file on the filesystem. I have no idea why this happens.
// const oldCwd = process.cwd;
process.cwd = () => join(dirname);
// process.cwd = oldCwd;

const postcssBuild = async () => {
    try {
        const css = await readFile(postcssOptions.from, {encoding: "utf-8"});
        const result = await cssProcessor.process(css, postcssOptions);

        await writeFile(postcssOptions.to, result.css);
        if (result.map) {
            await writeFile(postcssOptions.to + ".map", JSON.stringify(result.map.toJSON()));
        }
        console.log("Built css!")
    } catch (error) {
        console.log(error.toString?.() ?? error);
    }
}

if (process.argv.includes("-w") || process.argv.includes("--watch")) {
    console.log("Starting...");
    const ctx = await context(esbuildOptions);

    const rebuild = debounce(async () => {
        console.clear();
        console.time("Built in ");
        await Promise.all([
            // No need to do anything with this as ESBuild also logs it for us.
            ctx.rebuild().then(() => console.log("Built js!")).catch((_) => {
            }),
            postcssBuild()
        ]);
        console.timeEnd("Built in ");
    }, 300);

    const watcher = watch(join(dirname, "src"), {
        persistent: true
    });

    watcher.on("add", rebuild)
        .on("change", rebuild)
        .on("unlink", rebuild);
} else {
    console.time("Built in ");
    await Promise.all([
        build(esbuildOptions),
        postcssBuild()
    ]);
    console.timeEnd("Built in ");
}