export function getKeywords(){
    var keywordList = document.getElementsByTagName("highlight-term")

    for (let i = 0; i < keywordList.length; i++) {
        build_eventlistener(keywordList[i].id, keywordList[i].dataset.label, keywordList[i].dataset.line)
    }
}


export function build_eventlistener(command_id, code_box_label, code_line_number){
    // get the dynamic variables created by Hugo
    // var command_id = document.currentScript.getAttribute('rand_id');
    // var code_box_label = document.currentScript.getAttribute('label');
    // var code_line_number = document.currentScript.getAttribute('line');

    // the <mouseover> elment of the individual command calling the shortcode
    var command = document.getElementById(command_id);

    // the outer div for the fenced code block
    var code_box = document.querySelector("div[label=" + code_box_label + "]");

    // the element of the line number we want
    var code_line_num = code_box.getElementsByClassName("lnt")[code_line_number - 1 ];

    // the element of the source code text we want
    var code_line_text = code_box.getElementsByClassName("line")[code_line_number - 1 ];

    // create a new span element to wrap the line number in for highlighting
    var line_num_hl_span = document.createElement('span');
    line_num_hl_span.classList.add('hl');
    line_num_hl_span.setAttribute('id', 'hover-hl');

    command.addEventListener('mouseover', function handleMouseOver() {
        highlight_line(code_line_num, code_line_text, line_num_hl_span);

    });

    command.addEventListener('mouseout', function handleMouseOut() {
        remove_highlight_line(code_line_num, code_line_text, line_num_hl_span);
    });

}

function highlight_line(line_num, line_text, hl_span) {
    line_num.parentNode.insertBefore(hl_span, line_num);
    hl_span.appendChild(line_num);
    line_text.classList.toggle("hl");
}

function remove_highlight_line(line_num, line_text, hl_span){
    // get the element's parent node
    var parent = hl_span.parentNode;
    // move all children out of the element
    while (hl_span.firstChild) parent.insertBefore(hl_span.firstChild, hl_span);
    // remove the empty element
    parent.removeChild(hl_span);
    line_text.classList.toggle("hl");
}
