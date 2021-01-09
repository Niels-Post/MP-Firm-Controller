// Store the current state of the webpage
let state = {
    robotData: [],
    selectedRobot: null,
    history_last_message_type: null,
    history_current_message_group: null,
    scenario_status_interval: null,
    current_scenario_uuid: null,
    current_scenario_info: null
}

// API Endpoints
let api_routes = {
    robots: () => "/robot/all",
    robot_new_messages: (robot) => `/robot/${robot}/newmessages`,
    robot_move_mm: (robot, mm, direction) => `/robot/${robot}/move/${mm}/${direction}`,
    robot_rotate: (robot, degrees, direction) => `/robot/${robot}/rotate/${degrees}/${direction}`,
    scenarios: () => "/scenario/all",
    start_scenario: (robot, scenario_id) => `/scenario/run/${robot}/${scenario_id}`,
    scenario_status: (uuid) => `/scenario/status/${uuid}`,
    scenario_info: (scenario_id) => `/scenario/info/${scenario_id}`
}

// All templates for HTML elements that need to be inserted somewhere
let element_templates = {
    robotlist_item: $(`
        <div class="item">
            <img class="ui avatar image" src="https://cdn3.iconfinder.com/data/icons/avatars-9/145/Avatar_Robot-512.png">
            <div class="content">
                <div class="header"></div>
                <div class='content'></div>
            </div>
        </div>
    `),
    commandlog_commandgroup: $(`
        <div class="comment">
            <a class="avatar"><img src=""></a>
            <div class="content">
              <a class="author"></a>
              <div class='text'>
                <div class="ui divided list"></div>
              </div>
            </div>
        </div>`),
    commandlog_command: $(`
        <div class=item>
            <div class="ui red horizontal  label message_id">test</div>
            <div class="ui blue horizontal  label category"></div>
            <div class="text"></div>
        </div>`),
    testscenario_item: $(`
        <div class=item></div>
    `),
    testscenario_prop: $(`
        <tr>
            <td><div class="ui horizontal label"></div></td>
        </tr> 
    `),
    testscenario_value: $(`
        <td></td>
    `)
}

// Store all jQuery selectors on page load so we don't have to keep looking up
$(document).ready(() => {
    let currentRobotInfo = $("#currentRobotInfo")

    let testscenario_dropdown = $(".testscenarios")

    let testscenario_progress = $(".testscenario_progress");
    window.$$ = {
        currentRobotInfo: currentRobotInfo,
        currentRobotInfo_x: currentRobotInfo.find(".position .x"),
        currentRobotInfo_y: currentRobotInfo.find(".position .y"),
        currentRobotInfo_r: currentRobotInfo.find(".position .r"),
        selected_robot_name:  currentRobotInfo.find(".robotname"),
        robotSelection: $("#robotSelection"),
        comm_history: $("#history_view .comments"),
        input_mm_or_degree: $("#inp_mm_deg"),
        testscenario_dropdown: testscenario_dropdown,
        testscenario_dropdown_value: testscenario_dropdown.find(".dropdown_value"),
        testscenario_dropdown_content: testscenario_dropdown.find(".menu"),
        testscenario_progress: testscenario_progress,
        testscenario_progress_label: testscenario_progress.find(".label"),
        testscenario_results: $("#testscenario_results"),
        testscenario_results_dimmer: $("#testscenario_results_dimmer"),
        testscenario_description: $("#testscenario_description"),
        testscenario_prerequisites: $("#testscenario_prerequisites"),
        testscenario_values: $("#testscenario_values"),

    }
})



// Startup operations
$(document).ready(() => {
    initializeTestScenarios();

    setInterval(refreshData, 500)

    $("#btn_move_forward").click(() => {
        fetch(api_routes.robot_move_mm(state.selectedRobot, $$.input_mm_or_degree.val(), 1));
    })

    $("#btn_move_backward").click(() => {
        fetch(api_routes.robot_move_mm(state.selectedRobot, $$.input_mm_or_degree.val(), 0));
    })

    $("#btn_rotate_right").click(() => {
        fetch(api_routes.robot_rotate(state.selectedRobot, $$.input_mm_or_degree.val(), 1));
    })

    $("#btn_rotate_left").click(() => {
        fetch(api_routes.robot_rotate(state.selectedRobot, $$.input_mm_or_degree.val(), 0));
    })


    $("#testscenario_run").click(runTestScenario);
    $("#testscenario_info").click(showTestScenarioInfo);
})

function initializeTestScenarios() {
        $$.testscenario_dropdown.dropdown({
            onChange: showTestScenarioInfo
        });

        fetch(api_routes.scenarios())
            .then(response => response.json())
            .then(data => {
                for(let scenario of data['scenarios']) {
                    let testscenario_item = element_templates.testscenario_item.clone();
                    testscenario_item.html(scenario);
                    testscenario_item.data("value", scenario);
                    testscenario_item.appendTo($$.testscenario_dropdown_content);
                }
            })
}


/**
 * Retrieve new information from the Controller Server and update the web page correspondingly
 */
function refreshData() {
    fetch(api_routes.robots())
        .then(response => response.json())
        .then(data => {
            state.robotData = data.robots;
            updateRobotList();
            updateRobotPosition();
        })

    if (state.selectedRobot != null) {
        fetch(api_routes.robot_new_messages(state.selectedRobot))
            .then(response => response.json())
            .then(updateMessageLog);
    }
}

/**
 * Called when a robot is selected
 */
function selectRobot() {
    state.selectedRobot = $(this).data("id");
    $(this).addClass("active");
    $$.currentRobotInfo.find(".button").removeClass("disabled");
    $$.selected_robot_name.html("Robot " + state.selectedRobot);
    $$.comm_history.html("")
}

/**
 * Update the position display for the currently selected robot
 */
function updateRobotPosition() {
    if (state.selectedRobot == null || !state.robotData.hasOwnProperty(state.selectedRobot)) {
        return;
    }
    let x = Math.round(state.robotData[state.selectedRobot].current_pose.position[0] * 100)/100
    let y = Math.round(state.robotData[state.selectedRobot].current_pose.position[1] * 100)/100
    let r = Math.round(state.robotData[state.selectedRobot].current_pose.angle * 100)/100
    $$.currentRobotInfo_x.html(x)
    $$.currentRobotInfo_y.html(y)
    $$.currentRobotInfo_r.html(r)
}

/**
 * Update the list of robots
 */
function updateRobotList() {
    $$.robotSelection.html("");

    for (let id in state.robotData) {
        if (!state.robotData.hasOwnProperty(id)) {
            continue;
        }

        let robotlist_element = $(element_templates.robotlist_item);
        robotlist_element.find(".header").html("Robot " + id);
        robotlist_element.data("id", id);


        if (id === state.selectedRobot) {
            robotlist_element.attr("active", true);
            robotlist_element.addClass("positive");
        }

        robotlist_element.find(".content .content").html(state.robotData[id].state);

        robotlist_element.appendTo($$.robotSelection);

        robotlist_element.on('click', selectRobot);
    }
}

/**
 * Update the communication message view for the selected robot
 * @param messages Messages to append
 */
function updateMessageLog(messages) {
    for (let message of messages.messages) {
        if (message['type'] !== state.history_last_message_type) {
            state.history_last_message_type = message['type'];

            state.history_current_message_group = element_templates.commandlog_commandgroup.clone();
            state.history_current_message_group.appendTo($$.comm_history);
            $$.comm_history.append("<div class='ui divider'></div>")
            if (message['type'] === "command") {
                state.history_current_message_group.find(".avatar img").attr("src", "https://www.raspberrypi.org/wp-content/uploads/2011/10/Raspi-PGB001-300x267.png");
                state.history_current_message_group.find(".author").html("Controller");
            } else {
                state.history_current_message_group.find(".avatar img").attr("src", "https://cdn3.iconfinder.com/data/icons/avatars-9/145/Avatar_Robot-512.png");
                state.history_current_message_group.find(".author").html(`Robot ${state.selectedRobot}`);
            }

        }

        let current_message = element_templates.commandlog_command.clone();
        current_message.append(message['text'])
        current_message.find(".message_id").html(message['message_id'])
        current_message.find(".category").html(message['category'])
        current_message.appendTo(state.history_current_message_group.find(".list"))
        $$.comm_history.scrollTop($$.comm_history.prop("scrollHeight"))

    }
}


function runTestScenario() {
    if(state.selectedRobot == null) {
        return;
    }
     let testScenario = $$.testscenario_dropdown_value.val()
    fetch(api_routes.start_scenario(state.selectedRobot, testScenario))
        .then(response => response.json())
        .then(data => {
            state.current_scenario_uuid = data.uuid
            state.scenario_status_interval = setInterval(testScenarioStatus, 100);
            $$.testscenario_progress_label.html("Test Started");
            $$.testscenario_progress.removeClass("error");
            $$.testscenario_results_dimmer.addClass("active");
        })
}

function testScenarioStatus() {
    fetch(api_routes.scenario_status(state.current_scenario_uuid))
        .then(response => response.json())
        .then(data => {
            $$.testscenario_progress.progress({
                percent: data.percent_complete
            })

            if(data.finished) {
                if(state.scenario_status_interval != null) {
                    clearInterval(state.scenario_status_interval)
                    state.scenario_status_interval = null;
                }

                if(data.success) {
                    $$.testscenario_progress_label.html("Test Finished")
                    showTestScenarioResults(data.result)
                } else {
                    $$.testscenario_progress_label.html("Test errored");
                    $$.testscenario_progress.addClass("error");
                    $$.testscenario_results_dimmer.removeClass("active");

                }
            }

        })
}

function showTestScenarioResults(results) {
    $$.testscenario_results.html("")

    for(let prop in results) {
        if (!results.hasOwnProperty(prop)) {
            continue;
        }

        let prop_element = element_templates.testscenario_prop.clone();
        prop_element.find(".label").html(prop);

        if(!Array.isArray(results[prop])) {
            results[prop] = [results[prop]];
        }

        for (let value of results[prop]) {
            let column = element_templates.testscenario_value.clone();
            column.html(value.toString());
            column.appendTo(prop_element);
        }

        prop_element.appendTo($$.testscenario_results);
    }
    $$.testscenario_results_dimmer.removeClass("active");

}

function showTestScenarioInfo(text, info) {
    let id = $$.testscenario_dropdown_value.val()
    fetch(api_routes.scenario_info(id))
        .then(response => response.json())
        .then(information => {
            $$.testscenario_description.html(information.description);
            $$.testscenario_prerequisites.html(information.prerequisites)

            $$.testscenario_values.html("");

            for(let prop in information.results) {
                if (!information.results.hasOwnProperty(prop)) {
                    continue;
                }

                let prop_element = element_templates.testscenario_prop.clone();
                prop_element.find(".label").html(prop);

                let description = element_templates.testscenario_value.clone();
                description.html(information.results[prop]);
                description.appendTo(prop_element);

                prop_element.appendTo($$.testscenario_values);
            }
        });
}

