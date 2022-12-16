export function getKeywords(){
    var keywordList = document.getElementsByTagName("highlight-term")

    for (let i = 0; i < keywordList.length; i++) {
        build_eventlistener(keywordList[i].id, keywordList[i].dataset.label, keywordList[i].dataset.line)
    }
}


export function build_eventlistener(command_id, code_box_label, code_line_number){
    // get the dynamic variables created by Hugo shortcode
    // var command_id = document.currentScript.getAttribute('rand_id');
    // var code_box_label = document.currentScript.getAttribute('label');
    // var code_line_number = document.currentScript.getAttribute('line');

    // the <mouseover> elment of the individual command calling the shortcode
    var command = document.getElementById(command_id);

    // the outer div for the fenced code block
    var code_box = document.querySelector("div[label=" + code_box_label + "]");

    // the element of the source code text we want
    var code_line_text = code_box.getElementsByClassName("cl")[code_line_number - 1 ];

    command.addEventListener('mouseover', function handleMouseOver() {
        code_line_text.classList.toggle("hl");
    });

    command.addEventListener('mouseout', function handleMouseOut() {
        code_line_text.classList.toggle("hl");
    });

}

function toggle_highlight(line_num, line_text, hl_span) {
    line_text.classList.toggle("hl");
}

window.onload = getKeywords();