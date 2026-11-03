const assert = require("node:assert/strict");
const {test} = require("node:test");
const {readFileSync} = require("node:fs");
const vm = require("node:vm");
function run(status, responseText) {
    const output = {};
    let requested;
    const context = {
        document: {getElementById: id => id === "textToAnalyze" ? {value: "joy & fear? + ü"} : output},
        XMLHttpRequest: class {
            open(method, url) { requested = url; }
            send() { Object.assign(this, {readyState: 4, status, responseText}); this.onreadystatechange(); }
        }
    };
    vm.runInNewContext(readFileSync("static/mywebscript.js", "utf8") + "\nRunSentimentAnalysis();", context);
    return {output, requested};
}
test("input is URL encoded and only response text is rendered", () => {
    const {output, requested} = run(200, JSON.stringify({response: "<b>joy</b>"}));
    assert.equal(new URL(requested, "http://localhost").searchParams.get("textToAnalyze"), "joy & fear? + ü");
    assert.equal(output.textContent, "<b>joy</b>");
    assert.equal(output.innerHTML, undefined);
});
test("unavailable and invalid responses are visible", () => {
    assert.equal(run(503, JSON.stringify({response: "Temporarily unavailable"})).output.textContent, "Temporarily unavailable");
    assert.match(run(500, "not-json").output.textContent, /unavailable/);
});
