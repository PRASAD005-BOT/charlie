$(document).ready(function () {
    // Text animation using textillate
    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        }
    });

    // SiriWave configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: 1,
        speed: 0.30,
        autostart: true
    });

    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },
    });

    // Mic button click event
    $("#MicBtn").click(function () {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands();  // Trigger commands handling in Python
    });

    // Key up event for space to trigger assistant sound
    $(document).on('keyup', function (e) {
        if (e.key === ' ') {
            eel.playAssistantSound();
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands();
        }
    });

    // Function to play assistant
    function PlayAssistant(message) {
        if (message !== "") {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message);
            $("#chatbox").val(""); // Clear chatbox
            ShowHideButton(""); // Update mic/send button visibility
        }
    }

    // Toggle function to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length === 0) {
            $("#MicBtn").removeAttr('hidden');
            $("#SendBtn").attr('hidden', true);
        } else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").removeAttr('hidden');
        }
    }

    // Key up event handler on chatbox
    $("#chatbox").keyup(function () {
        let message = $(this).val();
        ShowHideButton(message);
    });

    // Send button event handler
    $("#SendBtn").click(function () {
        let message = $("#chatbox").val();
        PlayAssistant(message);
    });

    // Enter press event handler on chatbox
    $("#chatbox").keypress(function (e) {
        if (e.which === 13) { // Enter key
            let message = $(this).val();
            PlayAssistant(message);
        }
    });

    // Toggle settings panel visibility
    $('#SettingsBtn').click(function () {
        $('#settings-panels').toggle();
        $(this).toggleClass('active');
        $("#chatbot-container").hide();  // Hide chatbot when settings are opened
    });

    // Show the "System Path" panel by default
    $('.panel').hide();
    $('#system-path-panel').show();

    // Panel navigation
    $('.nav-btn').click(function () {
        var panelId = $(this).data('panel');
        $('.panel').hide();  // Hide all panels
        $(panelId).show();   // Show selected panel
        loadPanelData(panelId); // Load data for the selected panel
    });

    // Function to load panel data from local storage
    function loadPanelData(panelId) {
        switch (panelId) {
            case '#system-path-panel':
                loadSystemPaths();
                break;
            case '#website-panel':
                loadWebsites();
                break;
            case '#schedule-panel':
                loadSchedule();
                break;
            case '#chatbot-key-panel':
                loadChatbotKeys();
                break;
            case '#phonebook-panel':
                loadPhonebook();
                break;
        }
    }

    // Add system path
    $('#save-system-paths').click(function () {
        var name = $('#system-path-name').val();
        var path = $('#system-path').val();
        if (name && path) {
            appendSystemPath(name, path);
            saveSystemPath(name, path);
            $('#system-path-name').val('');
            $('#system-path').val('');
        } else {
            alert('Please fill in both fields.');
        }
    });

    // Delete system path event
    $(document).on('click', '.delete-system-path', function () {
        var row = $(this).closest('tr');
        var name = row.find('td').first().text();
        row.remove();
        removeSystemPath(name);
    });

    // Add website event
    $('#save-websites').click(function () {
        var name = $('#website-name').val();
        var url = $('#website-path').val();
        if (name && url) {
            appendWebsite(name, url);
            saveWebsite(name, url);
            $('#website-name').val('');
            $('#website-path').val('');
        } else {
            alert('Please fill in both fields.');
        }
    });

    // Delete website event
    $(document).on('click', '.delete-website', function () {
        var row = $(this).closest('tr');
        var name = row.find('td').first().text();
        row.remove();
        removeWebsite(name);
    });

    // Add schedule event
    $('#save-schedule').click(function () {
        var day = $('#day').val();
        var schedule = $('#schedule').val();
        if (day && schedule) {
            appendSchedule(day, schedule);
            saveSchedule(day, schedule);
            $('#day').val('');
            $('#schedule').val('');
        } else {
            alert('Please fill in both fields.');
        }
    });

    // Delete schedule event
    $(document).on('click', '.delete-schedule', function () {
        var row = $(this).closest('tr');
        var day = row.find('td').first().text();
        row.remove();
        removeSchedule(day);
    });

    // Add chatbot key event
    $('#save-chatbot-key').click(function () {
        var keyName = $('#key-name').val();
        var apiKey = $('#api-key').val();
        if (keyName && apiKey) {
            appendChatbotKey(keyName, apiKey);
            saveChatbotKey(keyName, apiKey);
            $('#key-name').val('');
            $('#api-key').val('');
        } else {
            alert('Please fill in both fields.');
        }
    });

    // Delete chatbot key event
    $(document).on('click', '.delete-chatbot-key', function () {
        var row = $(this).closest('tr');
        var keyName = row.find('td').first().text();
        row.remove();
        removeChatbotKey(keyName);
    });
    

    // Add phone number event
    $('#save-contacts').click(function () {
        var name = $('#contact-name').val();
        var number = $('#contact-phone').val();
        if (name && number && /^\d{10}$/.test(number)) {
            appendPhoneNumber(name, number);
            savePhoneNumber(name, number);
            $('#contact-name').val('');
            $('#contact-phone').val('');
        } else {
            alert('Please enter a valid 10-digit phone number.');
        }
    });

    // Delete phone number event
    $(document).on('click', '.delete-phone-number', function () {
        var row = $(this).closest('tr');
        var name = row.find('td').first().text();
        row.remove();
        removePhoneNumber(name);
    });

    // Function to save system paths
    function saveSystemPath(name, path) {
        let systemPaths = JSON.parse(localStorage.getItem('systemPaths')) || [];
        systemPaths.push({ name: name, path: path });
        localStorage.setItem('systemPaths', JSON.stringify(systemPaths));
        alert("Saved successfully!");
    }

    // Function to save websites
    function saveWebsite(name, url) {
        let websites = JSON.parse(localStorage.getItem('websites')) || [];
        websites.push({ name: name, url: url });
        localStorage.setItem('websites', JSON.stringify(websites));
        alert("Saved successfully!");
    }

    // Function to save schedule
    function saveSchedule(day, schedule) {
        let schedules = JSON.parse(localStorage.getItem('schedules')) || [];
        schedules.push({ day: day, schedule: schedule });
        localStorage.setItem('schedules', JSON.stringify(schedules));
        alert("Saved successfully!");
    }

    // Function to save chatbot keys
    function saveChatbotKey(keyName, apiKey) {
        let chatbotKeys = JSON.parse(localStorage.getItem('chatbotKeys')) || [];
        chatbotKeys.push({ keyName: keyName, apiKey: apiKey });
        localStorage.setItem('chatbotKeys', JSON.stringify(chatbotKeys));
        alert("Saved successfully!");
    }

    // Function to save phone numbers
    function savePhoneNumber(name, number) {
        let phonebook = JSON.parse(localStorage.getItem('phonebook')) || [];
        phonebook.push({ name: name, number: number });
        localStorage.setItem('phonebook', JSON.stringify(phonebook));
        alert("Saved successfully!");
    }

    // Function to load system paths from local storage
    function loadSystemPaths() {
        let systemPaths = JSON.parse(localStorage.getItem('systemPaths')) || [];
        $('#system-paths-list tbody').empty();
        systemPaths.forEach(path => {
            appendSystemPath(path.name, path.path);
        });
    }

    // Function to load websites from local storage
    function loadWebsites() {
        let websites = JSON.parse(localStorage.getItem('websites')) || [];
        $('#websites-list tbody').empty();
        websites.forEach(website => {
            appendWebsite(website.name, website.url);
        });
    }

    // Function to load schedule from local storage
    function loadSchedule() {
        let schedules = JSON.parse(localStorage.getItem('schedules')) || [];
        $('#schedule-list tbody').empty();
        schedules.forEach(schedule => {
            appendSchedule(schedule.day, schedule.schedule);
        });
    }

    // Function to load chatbot keys from local storage
    function loadChatbotKeys() {
        let chatbotKeys = JSON.parse(localStorage.getItem('chatbotKeys')) || [];
        $('#chatbot-keys-list tbody').empty();
        chatbotKeys.forEach(key => {
            appendChatbotKey(key.keyName, key.apiKey);
        });
    }

    // Function to load phonebook from local storage
    function loadPhonebook() {
        let phonebook = JSON.parse(localStorage.getItem('phonebook')) || [];
        $('#phonebook-list tbody').empty();
        phonebook.forEach(contact => {
            appendPhoneNumber(contact.name, contact.number);
        });
    }
    function getAllLocalStorageData() {
        // Retrieve data from local storage
        let data = {
            'SystemPath': JSON.parse(localStorage.getItem('systemPaths')) || [],
            'Website': JSON.parse(localStorage.getItem('websites')) || [],
            'Phonebook': JSON.parse(localStorage.getItem('phonebook')) || [],
            'ChatbotKeys': JSON.parse(localStorage.getItem('chatbotKeys')) || [],
            'Schedule': JSON.parse(localStorage.getItem('schedules')) || []
        };
    
        // Debugging: Log the data being sent
        
    
        // Send the data to Python
        eel.receiveLocalStorageData(data)();
    }
    
    // Call this function when you want to send all data to Python
    getAllLocalStorageData();
    function getspotifydata() {
        let data = {
            'ChatbotKeys': JSON.parse(localStorage.getItem('chatbotKeys')) || []
        };
        eel.spotify(data)();
    }
    getspotifydata();
    function getweatherdata() {
        let data = {
            'ChatbotKeys': JSON.parse(localStorage.getItem('chatbotKeys')) || []
        };
        eel.weather(data)();
    }
    getweatherdata();
    function getscheduledata(){
        let data = {
            'Schedule': JSON.parse(localStorage.getItem('schedules')) || []
        };
        eel.scheduled(data)();
    
    }
    getscheduledata()
    // Function to append a system path to the table
    function appendSystemPath(name, path) {
        $('#system-paths-list tbody').append(`
            <tr>
                <td>${name}</td>
                <td>${path}</td>
                <td><button class="btn btn-danger btn-sm delete-system-path">Delete</button></td>
            </tr>
        `);
    }

    // Function to append a website to the table
    function appendWebsite(name, url) {
        $('#websites-list tbody').append(`
            <tr>
                <td>${name}</td>
                <td>${url}</td>
                <td><button class="btn btn-danger btn-sm delete-website">Delete</button></td>
            </tr>
        `);
    }

    // Function to append a schedule to the table
    function appendSchedule(day, schedule) {
        $('#schedule-list tbody').append(`
            <tr>
                <td>${day}</td>
                <td>${schedule}</td>
                <td><button class="btn btn-danger btn-sm delete-schedule">Delete</button></td>
            </tr>
        `);
    }
    function appendChatbotKey(keyName, apiKey) {
        const tableBody = document.querySelector('#chatbot-keys-list tbody');
        const newRow = document.createElement('tr');

        newRow.innerHTML = `
            <td>${keyName}</td>
            <td>
                <span class="api-key">${apiKey}</span>
                <span class="api-key-hidden">••••••••••</span>
            </td>
            <td><button class="btn btn-warning btn-sm" onclick="toggleKeyVisibility(this)">Show/Hide</button></td>
            <td><button class="btn btn-danger btn-sm delete-chatbot-key" onclick="deleteChatbotKey(this)">Delete</button></td>
        `;

        tableBody.appendChild(newRow);
        // Initially hide the API key
        hideApiKeyInRow(newRow);
    }
     // Function to delete a chatbot key
     function deleteChatbotKey(button) {
        const row = button.closest('tr');
        row.remove();
    }

    // Function to toggle key visibility
    window.toggleKeyVisibility = function(button) {
        const row = button.closest('tr');
        const apiKeySpan = row.querySelector('.api-key');
        const apiKeyHiddenSpan = row.querySelector('.api-key-hidden');

        if (apiKeySpan.style.display === 'none' || apiKeySpan.style.display === '') {
            apiKeySpan.style.display = 'inline';
            apiKeyHiddenSpan.style.display = 'none';
        } else {
            apiKeySpan.style.display = 'none';
            apiKeyHiddenSpan.style.display = 'inline';
        }
    };

    // Function to hide the API key in a row
    function hideApiKeyInRow(row) {
        const apiKeySpan = row.querySelector('.api-key');
        const apiKeyHiddenSpan = row.querySelector('.api-key-hidden');

        apiKeySpan.style.display = 'none';
        apiKeyHiddenSpan.style.display = 'inline';
    }
       


    // Event listener for saving chatbot keys
    document.getElementById('save-chatbot-key').addEventListener('click', function() {
        const keyName = document.getElementById('key-name').value;
        const apiKey = document.getElementById('api-key').value;

        if (keyName && apiKey) {
            appendChatbotKey(keyName, apiKey);
            // Clear input fields
            document.getElementById('key-name').value = '';
            document.getElementById('api-key').value = '';
        } 
    });


    // Function to append a phone number to the table
    function appendPhoneNumber(name, number) {
        $('#phonebook-list tbody').append(`
            <tr>
                <td>${name}</td>
                <td>${number}</td>
                <td><button class="btn btn-danger btn-sm delete-phone-number">Delete</button></td>
            </tr>
        `);
    }

    // Function to remove a system path from local storage
    function removeSystemPath(name) {
        let systemPaths = JSON.parse(localStorage.getItem('systemPaths')) || [];
        systemPaths = systemPaths.filter(path => path.name !== name);
        localStorage.setItem('systemPaths', JSON.stringify(systemPaths));
        alert("Deleted successfully!");
    }

    // Function to remove a website from local storage
    function removeWebsite(name) {
        let websites = JSON.parse(localStorage.getItem('websites')) || [];
        websites = websites.filter(website => website.name !== name);
        localStorage.setItem('websites', JSON.stringify(websites));
        alert("Deleted successfully!");
    }

    // Function to remove a schedule from local storage
    function removeSchedule(day) {
        let schedules = JSON.parse(localStorage.getItem('schedules')) || [];
        schedules = schedules.filter(schedule => schedule.day !== day);
        localStorage.setItem('schedules', JSON.stringify(schedules));
        alert("Deleted successfully!");
    }

    // Function to remove a chatbot key from local storage
    function removeChatbotKey(keyName) {
        let chatbotKeys = JSON.parse(localStorage.getItem('chatbotKeys')) || [];
        chatbotKeys = chatbotKeys.filter(key => key.keyName !== keyName);
        localStorage.setItem('chatbotKeys', JSON.stringify(chatbotKeys));
        alert("Deleted successfully!");
    }

    function removePhoneNumber(name) {
        let phonebook = JSON.parse(localStorage.getItem('phonebook')) || [];
        phonebook = phonebook.filter(contact => contact.name !== name);
        localStorage.setItem('phonebook', JSON.stringify(phonebook));
        alert("Deleted successfully!");
    }
});