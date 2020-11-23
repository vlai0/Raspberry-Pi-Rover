//create the joystick to control the rover
joystick = buildJoystick(document.getElementById('base'));

//vars
var positions = [];
joystickEnabled = true;
collAvoid = true;
var distButton = $("distance");
//enum/class for direction to prevent messing with the servo through the keyboard
const directions = {
	LEFT: 'left',
	RIGHT: 'right',
	STRAIGHT: 'straight'
}
direction = directions.STRAIGHT;

//event listeners
document.addEventListener('keydown', keyDown);
document.addEventListener('keyup', keyUp);

//to constantly update joystick
setInterval(updateMovement, 20);

function keyDown(e) {
	joystickEnabled = false;
	if (e.code == "KeyW") {
		drive();
		getDist();
	}
	if (e.code == "KeyS") {
		reverse();
	}
	if (e.code == "KeyA" && direction != directions.RIGHT) {
		left();
		direction = directions.LEFT;
	}
	if (e.code == "KeyD" && direction != directions.LEFT) {
		right();
		direction = directions.RIGHT;
	}
}

function keyUp(e) {
	if (e.code == "KeyW" || e.code == "KeyS") {
		neutral();
	}
	if (e.code == "KeyA" || e.code == "KeyD") {
		straight();
		direction = directions.STRAIGHT;
	}
}

//function to update joystick position and control movement
function updateMovement() {
	positions = joystick.getPosition();
	//left, straight, or right
	if (positions[0] < -30) {
		joystickEnabled = true;
		left();
	}
	if (positions[0] >= -30 && positions[0] <= 30 && joystickEnabled == true) {
		straight();
	}
	if (positions[0] > 30) {
		joystickEnabled = true;
		right();
	}
	//drive, neutral, reverse
	if (positions[1] > 30) {
		joystickEnabled = true;
		drive();
		getDist();
	}
	if (positions[1] >= -30 && positions[1] <= 30 && joystickEnabled == true) {
		neutral();
	}
	if (positions[1] < -30) {
		joystickEnabled = true;
		reverse();
	}
}

//functions for movement and direction
function drive() {
	$.ajax({
		url: "/drive",
		type: "post",
		success: function(response) {
			console.log("drive");
		}
	});
}
function neutral() {
	$.ajax({
		url: "/neutral",
		type: "post",
		success: function(response) {
			console.log("neutral");
		}
	});
}
function reverse() {
	$.ajax({
		url: "/reverse",
		type: "post",
		success: function(response) {
			console.log("reverse");
		}
	});
}
function left() {
	$.ajax({
		url: "/left",
		type: "post",
		success: function(response) {
			console.log("left");
		}
	});
}
function straight() {
	$.ajax({
		url: "/straight",
		type: "post",
		success: function(response) {
			console.log("straight");
		}
	});
}
function right() {
	$.ajax({
		url: "/right",
		type: "post",
		success: function(response) {
			console.log("right");
		}
	});
}

function getDist() {
	$.ajax({
		url: "/get_dist",
		type: "post",
		success: function(response) {
			if (response == true && collAvoid == true) {
				neutral();
				reverse();
				setTimeout(() => {  neutral(); }, 300); //reverse for .3 seconds
			}
		}
	});
}

//button, i do want to make it change the class instead of text
distButton.click(function() {
    if (distButton.text() === "Disable Collision Avoidance") {
        distButton.text("Enable Collision Avoidance");
		collAvoid = false;
    } else {
        distButton.text("Disable Collision Avoidance");
		collAvoid = true;
    }
});

//joystick
function buildJoystick(parent) {
	const range = 100;
	circle = document.createElement('div');
	circle.classList.add('joystick'); //for css

	//set event listeners for touch and mouse
	//put on doc to allow for x and y coords
	circle.addEventListener('mousedown', mouseDown);
	document.addEventListener('mousemove', mouseMove);
	document.addEventListener('mouseup', mouseUp);
	circle.addEventListener('touchstart', mouseDown);
	document.addEventListener('touchmove', mouseMove);
	document.addEventListener('touchend', mouseUp);

	//vars to determine when it is dragging and the starting position
	dragging = false;
	startX = 0;
	startY = 0;
	position = [0, 0]; //array to return position

	function mouseDown(event) {
		//touch/mobile
		if (event.changedTouches) {
			dragging = true;
			//first touch point at index 0
			startX = event.changedTouches[0].clientX;
			startY = event.changedTouches[0].clientY;
		  return;
		}
		//mouse
		dragging = true;
		startX = event.clientX;
		startY = event.clientY;
	}

	function mouseUp(event) {
		//if it was never clicked end since the listener is on whole doc
		if (dragging == false) {
			return;
		}
		circle.style.transform = `translate3d(0px, 0px, 0px)`;
		dragging = false;
		startX = 0;
		startY = 0
		position = [0, 0];
	}

	function mouseMove(event) {
		//if it was never clicked since listener is on doc
		if (dragging == false) {
		  return;
		}
		currentX = event.clientX;
		currentY = event.clientY;
		//if it was touch it will set current coords to touch coords instead
		if (event.changedTouches) {
		  currentX = event.changedTouches[0].clientX;
		  currentY = event.changedTouches[0].clientY;
		}
		//find the difference
		changeX = currentX - startX;
		changeY = currentY - startY;
		//get the angle and distance travelled
		angle = Math.atan2(changeY, changeX);
		distance = Math.min(range, Math.hypot(changeX, changeY));
		updatedX = distance * Math.cos(angle);
		updatedY = distance * Math.sin(angle);
		circle.style.transform = `translate3d(${updatedX}px, ${updatedY}px, 0px)`;
		position[0] = updatedX;
		position[1] = -updatedY;
	}

	parent.appendChild(circle);
	return {
		getPosition: () => position,
	};
}
