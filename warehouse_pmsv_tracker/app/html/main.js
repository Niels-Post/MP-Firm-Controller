// Store the current state of the webpage
let state = {
    robotData: [],
    last_refresh_ids: "",
    selectedRobot: null,
    history_last_message_type: null,
    history_current_message_group: null,
    scenario_status_interval: null,
    current_scenario_uuid: null,
    current_scenario_info: null,
    configurationvalues: {},
    changed_configuration_values: {}
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Helper function for fetching json
 *
 * Continuously fetches a JSON object from an url until a condition becomes true
 * @param url Url to fetch from
 * @param condition Lambda condition (obj) -> bool. Should return true when the desired criterium is met
 * @param n Amount of times to retry before throwing an error
 * @returns {Promise<result>}
 */
async function fetch_json_until(url, condition, n = 100) {
    for (let i = 0; i < n; i++) {
        let result = await fetch_json(url);
        if (condition(result)) {
            return result;
        }
        await sleep(500);
    }
    throw Error("Failed fetch_json_until")
}


/**
 * Simple wrapper function to fetch JSON objects from an url
 * @param url Url to fetch
 * @returns {Promise<object>}
 */
async function fetch_json(url) {
    return new Promise(
        (res, rej) => {
            fetch(url)
                .then(response => response.json())
                .then(data => res(data));
        }
    )
}

// All API Endpoints
let api_routes = {
    robots: () => "/robot/all",
    robot_new_messages: (robot) => `/robot/${robot}/newmessages`,
    robot_move_mm: (robot, mm, direction) => `/robot/${robot}/move/${mm}/${direction}`,
    robot_rotate: (robot, degrees, direction) => `/robot/${robot}/rotate/${degrees}/${direction}`,
    scenarios: () => "/scenario/all",
    start_scenario: (robot, scenario_id) => `/scenario/run/${robot}/${scenario_id}`,
    scenario_status: (uuid) => `/scenario/status/${uuid}`,
    scenario_info: (scenario_id) => `/scenario/info/${scenario_id}`,
    config_request_valueinfo: (robot, config_id) => `/config/request_value_information/${robot}/${config_id}`,
    config_get_valueinfo: (robot, config_id) => `/config/get_value_information/${robot}/${config_id}`,
    config_get_all_valueinfo: (robot) => `/config/get_all_value_information/${robot}`,
    config_sync_information: (robot) => `/config/sync_value_information/${robot}`,
    config_set_value: (robot, config_id, value) => `/config/set_value/${robot}/${config_id}/${value}`,
    config_store_reboot: (robot) => `/config/store_and_reboot/${robot}`
}

// All templates for HTML elements that need to be inserted somewhere
let element_templates = {
    robotlist_item: $(`
        <div class="item robotselection_item">
            <img class="ui avatar image" src="https://cdn3.iconfinder.com/data/icons/avatars-9/145/Avatar_Robot-512.png">
            <div class="content">
                <div class="header">
                    
                </div>
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
    `),
    robotsettings_modal_configvalue_item: $(`
        <div class="eight wide column configvalue_item">
            <table class="robot_setting ui table">
            <tr>
                <td>
                    <div style="padding-left: 10px;">
                        (<span class="config_id">0</span>) <span class="config_name"></span>
                    </div>
                </td>
                <td>                     
                    <div class="ui fluid icon input">
                        <input class="value_value" type="text" placeholder="val">
                        <i class="asterisk gone icon"></i>
                    </div>
                </td>
            </tr>
            </table>
           
            </div>
            
        </div>
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
        selected_robot_name: currentRobotInfo.find(".robotname"),
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
        robotsettings_modal: $("#robotsettingsmodal"),
        robotsettings_modal_configlist: $("#configvalue_list")
    }
})


// Startup operations
$(document).ready(() => {
    initializeTestScenarios();

    setInterval(refreshData, 500)

    $(".settings_button").click(onRobotSettingsClicked)
    $(".remove_button").click(removeRobot)

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

    $("#robotsettings_applybutton").click(applyChangedRobotsettings)

    $("#robotsettings_storebutton").click(storeChangedRobotsettings)

    $("#robotsettings_restorebutton").click(restoreChangedRobotSettings)


    $("#testscenario_run").click(runTestScenario);
    $("#testscenario_info").click(showTestScenarioInfo);
})

/**
 * Fetch all available test scenario's and populate the test scenario dropdown
 */
function initializeTestScenarios() {
    $$.testscenario_dropdown.dropdown({
        onChange: showTestScenarioInfo
    });

    fetch(api_routes.scenarios())
        .then(response => response.json())
        .then(data => {
            for (let scenario of data['scenarios']) {
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
 * Load the configuration value names and populate the settings modal
 * @param result Data to populate with
 * @returns {Promise<void>}
 */
async function loadConfigNames(result) {
    $$.robotsettings_modal_configlist.html("");
    state.changed_configuration_values = {}
    state.configurationvalues = result;

    for (let configId in result) {
        if (!result.hasOwnProperty(configId)) {
            continue;
        }

        let configValue = result[configId];
        let item_element = element_templates.robotsettings_modal_configvalue_item.clone();
        item_element.attr("data-config_id", configValue.id);
        item_element.find(".config_id").html(configValue.id);


        item_element.appendTo($$.robotsettings_modal_configlist);


        item_element.find(".value_value").on('keyup', null, [configId, item_element], (evt) => {

            let input = evt.data[1].find(".value_value");
            let new_value = input.val();

            if (new_value !== state.configurationvalues[evt.data[0]].value.toString()) {
                item_element.find(".icon.asterisk").removeClass("gone");
                state.changed_configuration_values[evt.data[0]] = new_value;
            } else {
                item_element.find(".icon.asterisk").addClass("gone");
                if (state.changed_configuration_values.hasOwnProperty(evt.data[0])) {
                    delete state.changed_configuration_values[evt.data[0]]
                }
            }

        });

        item_element.find(".value_value").val(configValue.value);
        item_element.find(".config_name").html(configValue.name);
    }


}


/**
 * Called when a robot is selected
 */
async function selectRobot() {
    if (state.selectedRobot === $(this).data("id")) {
        return;
    }

    state.selectedRobot = $(this).data("id");
    $(this).addClass("active");
    $$.currentRobotInfo.find(".button").removeClass("disabled");
    $$.selected_robot_name.html("Robot " + state.selectedRobot);
    $$.comm_history.html("")

    fetch(api_routes.config_sync_information(state.selectedRobot));

    setTimeout(async () => {
        let data = await fetch_json_until(api_routes.config_get_all_valueinfo(state.selectedRobot), data => data.success)
        loadConfigNames(data['result']);
    }, 1000)
}

/**
 * Update the position display for the currently selected robot
 */
function updateRobotPosition() {
    if (state.selectedRobot == null || !state.robotData.hasOwnProperty(state.selectedRobot)) {
        return;
    }
    let x = Math.round(state.robotData[state.selectedRobot].current_pose.position[0] * 100) / 100
    let y = Math.round(state.robotData[state.selectedRobot].current_pose.position[1] * 100) / 100
    let r = Math.round(state.robotData[state.selectedRobot].current_pose.angle * 100) / 100
    $$.currentRobotInfo_x.html(x)
    $$.currentRobotInfo_y.html(y)
    $$.currentRobotInfo_r.html(r)
}

/**
 * Apply all robot settings that were changed in the settings modal
 * @returns {Promise<void>}
 */
async function applyChangedRobotsettings() {
    for (let config_id in state.changed_configuration_values) {
        if (!state.changed_configuration_values.hasOwnProperty(config_id)) {
            continue;
        }

        await fetch_json(api_routes.config_set_value(state.selectedRobot, config_id, state.changed_configuration_values[config_id]));

        state.configurationvalues[config_id].value = state.changed_configuration_values[config_id]

        $$.robotsettings_modal.find(`.configvalue_item[data-config_id=${config_id}] .icon.asterisk`).addClass("gone");

        await sleep(100);
    }

    state.changed_configuration_values = {};
}

/**
 * Store all current robot settings
 * @returns {Promise<void>}
 */
async function storeChangedRobotsettings() {
    fetch(api_routes.config_store_reboot(state.selectedRobot));
}

/**
 * Load all robot settings from the ROM (discarding changes)
 * @returns {Promise<void>}
 */
async function restoreChangedRobotSettings() {
    for (let config_id in state.changed_configuration_values) {
        if (!state.changed_configuration_values.hasOwnProperty(config_id)) {
            continue;
        }

        $$.robotsettings_modal.find(`.configvalue_item[data-config_id=${config_id}] .asterisk.icon`).addClass("gone");
        $$.robotsettings_modal.find(`.configvalue_item[data-config_id=${config_id}] .value_value`).val(state.configurationvalues[config_id].value);
    }
    state.changed_configuration_values = {};
}

/**
 * Open the robot settings modal
 * @returns {Promise<void>}
 */
async function onRobotSettingsClicked() {
    $$.robotsettings_modal.find(".robot_id").html(state.selectedRobot)
    $$.robotsettings_modal.modal('show');
}

function removeRobot() {

}

/**
 * Update the list of robots
 */
function updateRobotList() {

    let ids = []
    for (let id in state.robotData) {
        if (!state.robotData.hasOwnProperty(id)) {
            continue;
        }
        ids.push(id);
    }
    let current_refresh_ids = ids.sort().join(",")

    if (current_refresh_ids !== state.last_refresh_ids) {

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


            robotlist_element.appendTo($$.robotSelection);

            robotlist_element.on('click', selectRobot);
        }
    }

    $(".robotselection_item").each(function () {
        $(this).find(".content .content").html(state.robotData[$(this).data("id")].current_state)
    })

    state.last_refresh_ids = current_refresh_ids


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
    if (state.selectedRobot == null) {
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

/**
 * Retrieve the status of the currently running testscenario and update the progress bar
 */
function testScenarioStatus() {
    fetch(api_routes.scenario_status(state.current_scenario_uuid))
        .then(response => response.json())
        .then(data => {
            $$.testscenario_progress.progress({
                percent: data.percent_complete
            })

            if (data.finished) {
                if (state.scenario_status_interval != null) {
                    clearInterval(state.scenario_status_interval)
                    state.scenario_status_interval = null;
                }

                if (data.success) {
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

/**
 * Show the results of a testscenario
 * @param results
 */
function showTestScenarioResults(results) {
    $$.testscenario_results.html("")

    for (let prop in results) {
        if (!results.hasOwnProperty(prop)) {
            continue;
        }

        let prop_element = element_templates.testscenario_prop.clone();
        prop_element.find(".label").html(prop);

        if (!Array.isArray(results[prop])) {
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

/**
 * Display info about a test scenario
 */
function showTestScenarioInfo() {
    let id = $$.testscenario_dropdown_value.val()
    fetch(api_routes.scenario_info(id))
        .then(response => response.json())
        .then(information => {
            $$.testscenario_description.html(information.description);
            $$.testscenario_prerequisites.html(information.prerequisites)

            $$.testscenario_values.html("");

            for (let prop in information.results) {
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

