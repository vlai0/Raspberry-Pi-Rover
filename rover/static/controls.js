joystick = buildJoystick(document.getElementById('base'));

//setInterval(() => console.log(joystick.getPosition()), 16);

//joystick:
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
