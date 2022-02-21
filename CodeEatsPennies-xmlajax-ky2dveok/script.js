// Do some stuff when page hmtl page is launched
$(document).ready(function () {

    $("#headerTitle").hide(300).show(1500);
    // calling show food menu function
    showFoodMenu();
    
    // If you want to fetch data from the file 
    // call fetch data function instead of showFoodMenu
    // fetchData()
});

// ***************************************************************************************
// this function calls showfoodmenu 3000 milisecond to get new changes                   *
// made on demo.xml                                                                      *
// ***************************************************************************************
function fetchData() {
    setTimeout(function () {
        showFoodMenu();
        // recursive call
        fetchData();
    }, 3000);
}

// **************************************************************************************
// read data from demo.xml using Jquery | AJAX                                          *
// **************************************************************************************
function showFoodMenu() {

    $.ajax({
        type: "GET",
        url: "./demo.xml",
        dataType: "xml",

        error: function (e) {
            alert("An error occurred while processing XML file");
            console.log("XML reading Failed: ", e);
        },

        success: function (response) {

            // make sure the ul is empty
            // before appending data inot it
            $("ul").children().remove();

            $(response).find("food").each(function () {
                var _name = 'Name: ' + $(this).find('name').text();
                console.log(_name);
                
                var _price = 'Price: ' + $(this).find('price').text();
                var _calories = 'Calories: ' + $(this).find('calories').text();
                var _description = 'Description: ' + $(this).find('description').text();

                // add content to the HTML          
                $("ul").append('<li>' + _name + '</li>');
                $("ul").append('<li>' + _price + '</li>');
                $("ul").append('<li>' + _calories + '</li>');
                $("ul").append('<li>' + _description + '</li>');
            });
        }
    });
}