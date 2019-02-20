var assignments = {};
var curr_assignment;

$(document).ready(function(){
	$(".collapse-able").click(function(){
		var id = $(this).attr("id");
		var child_id = id + "-children";
		if($(this).hasClass("collapsed")){
			$(this).removeClass("collapsed");
			$("#"+child_id).hide();
		}
		else{
			$(this).addClass("collapsed");
			$("#"+child_id).show();
		}
	});

	// show assignment detail
	$("#assignments-children li").click(function(){
		var id = $(this).context.id;
		var assignment = assignments[id];

		$("#assignment-name").html(assignment.name);
		$("#assignment-author").html("Owner: " + assignment.owner_name);
		$("#assignment-query").html("Query: " + assignment.query);
		$("#assignment-ranker").html("Ranker: " + assignment.ranker);
		$("#assignment-deadline").html("Deadline: " + assignment.deadline);

		$('#content-welcome').hide();
		$("#content-assignment").show();

		curr_assignment = assignment;

		// remind user if this assignment have been finished already
		if(curr_assignment.complete) {
            // Allow re-submission
            // $("#nav-assignment-btn").css("display", "none");
            $("#nav-assignment-btn").html("Resubmit");
            $("#complete-text").css("display", "block");
		} else {
            $("#complete-text").css("display", "none");
		    $("#nav-assignment-btn").css("display", "inline-block");
            $("#nav-assignment-btn").html("Start");
        }
	});

	// go to assignment
	$("#nav-assignment-btn").click(function(){
		if($(this).html() == "Start Over"){
			$("#alert-modal").modal('show');
			return;
		}

		window.location = "/assignment/" + curr_assignment.owner_id + "/" + curr_assignment.name;
	});

	$("#nav-assignment-modal-btn").click(function(){
		window.location = "/assignment/" + curr_assignment.owner_id + "/" + curr_assignment.name;
	});
});
