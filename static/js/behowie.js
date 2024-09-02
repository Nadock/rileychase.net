//    function behowie() {
//        var button = document.querySelector("#behowie_button");
//        console.log(button);
//
//        navigator.mediaDevices.getUserMedia({ video: true });
//    }

//(() => {
//    // Code from: https://developer.mozilla.org/en-US/docs/Web/API/Media_Capture_and_Streams_API/Taking_still_photos
//
//
//    // |streaming| indicates whether or not we're currently streaming
//    // video from the camera. Obviously, we start at false.
//
//    let streaming = false;
//    let cameraFace = "user"
//
//    // The various HTML elements we need to configure or control. These
//    // will be set by the startup() function.
//
//    let video = null;
//    let canvas = null;
//
//    let startButton = null;
//    let flipButton = null;
//    let captureButton = null;
//

(() => {
    window.addEventListener("load", () => {
        document.getElementById("startButton").onclick = start;
    }, false);
})();

function start() {
    const canvas = document.getElementById("canvas")
    const video = document.getElementById("video");
    let face = "user";

    function flip() {
        return new Promise(async (resolve, reject) => {
            before = face
            face = face === "user" ? "environment" : "user";

            console.log(`flip camera from ${before} to ${face}`)
            await attachCamera(video, face).catch((e) => { reject(e) });

            resolve();
        })
    }

    function capture() {
        return new Promise(async (resolve, reject) => {
            let imgA = document.getElementById("userPhoto");
            let imgB = document.getElementById("environmentPhoto");

            // Set video stream to user image
            before = face;
            face = "user";
            await attachCamera(video, face);

            // Capture user image
            await captureImage(video, canvas, imgA);

            // Flip to the environment camera
            await flip();

            // Capture the environment image
            await captureImage(video, canvas, imgB);

            // Flip camera back to original face
            face = before;
            await attachCamera(video, face);

            resolve();
        })
    }

    attachCamera(video, face).then(() => {
        let startButton = document.getElementById("startButton");
        let flipButton = document.getElementById("flipButton");
        let captureButton = document.getElementById("captureButton");

        startButton.setAttribute("class", "camera--button hidden");
        flipButton.setAttribute("class", "camera--button");
        captureButton.setAttribute("class", "camera--button");

        flipButton.onclick = flip;
        captureButton.onclick = capture;
    });

};

// attachCamera gets a user media device, attaches it to the video element, and starts playback.
//
// `video` must be a `<video>` DOM element.
// `face` must a supported media devices facing mode, i.e. `"user"` or `"environment"`.
function attachCamera(video, face) {
    return new Promise(async (resolve, reject) => {
        if (video.srcObject !== null) {
            console.log(`stopping previous video stream ${video.srcObject}`);
            await video.srcObject.getTracks().forEach((track) => { track.stop() });
        }

        if (navigator.mediaDevices === null) {
            reject("navigator.mediaDevices is null, probably not in a secure context");
            return;
        }

        width = video.getBoundingClientRect().width;
        height = video.getBoundingClientRect().height;

        await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: face,
                width: { ideal: width },
                height: { ideal: height },
            },
            audio: false,
        }).then((stream) => {
            video.srcObject = stream;
            video.play();
            console.log(`camera ${stream} attached to ${video}`);
        }).catch((err) => {
            console.error(`an error occurred while attempting to start user media playback: ${err}`)
            reject(err);
        });

        resolve();
    })
};



function sleep(ms) {
    return new Promise((resolve) => { setTimeout(resolve, ms) });
}

function captureImage(video, canvas, image) {
    return new Promise((resolve, reject) => {
        // Get the video dimensions
        width = video.getBoundingClientRect().width;
        height = video.getBoundingClientRect().height;

        // Draw a frame onto the canvas
        const context = canvas.getContext("2d");
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);

        // Export the frame from the canvas to the image's src
        const data = canvas.toDataURL("image/png");
        image.setAttribute("src", data);

        resolve();
    });
};


//    function startup() {
//        video = document.getElementById("video");
//        canvas = document.getElementById("canvas");
//
//        startButton = document.getElementById("startButton");
//        flipButton = document.getElementById("flipButton");
//        captureButton = document.getElementById("captureButton");
//
//        width = document.getElementById("video-container").getBoundingClientRect().width * 0.9;
//        width = 400;
//        height = width * (19.5 / 9);
//        console.log(`width=${width} x height=${height}`)
//
//        attachCamera();
//
//        video.addEventListener(
//            "canplay",
//            (ev) => {
//                if (!streaming) {
//                    // Get the actual dimensions of the video container
//                    width = video.getBoundingClientRect().width;
//                    height = video.getBoundingClientRect().height;
//                    video.setAttribute("height", height);
//                    canvas.setAttribute("width", width);
//                    canvas.setAttribute("height", height);
//
//                    startButton.setAttribute("class", "camera--button hidden")
//                    flipButton.setAttribute("class", "camera--button")
//                    captureButton.setAttribute("class", "camera--button")
//
//                    streaming = true;
//                }
//            },
//            false,
//        );
//
//        captureButton.addEventListener(
//            "click",
//            (ev) => {
//                var userPhoto = document.getElementById("userPhoto");
//                var environmentPhoto = document.getElementById("environmentPhoto");
//
//                // Capture first image
//                captureImage(userPhoto);
//
//                // Flip to other camera and capture second image
//                flip();
//                setTimeout(5000);
//                captureImage(environmentPhoto);
//
//                // Flip back to the original camera
//                flip();
//
//                ev.preventDefault();
//            },
//            false,
//        );
//
//        flipButton.addEventListener("click", (ev) => {
//            flip();
//            ev.preventDefault();
//        }, false);
//
//    }
//
//    function flip() {
//        var before = cameraFace;
//        cameraFace = cameraFace === "environment" ? "user" : "environment";
//        console.log(`flipping cameraFace from ${before} to ${cameraFace}`)
//        attachCamera();
//    }
//
//    function attachCamera() {
//        console.log(`attaching to ${cameraFace} camera`)
//
//        if (video.srcObject !== null) {
//            console.log(`stopping previous video stream ${video.srcObject}`);
//            video.srcObject.getTracks().forEach((track) => { track.stop() });
//        }
//
//        navigator.mediaDevices
//            .getUserMedia({
//                video: {
//                    facingMode: cameraFace,
//                    width: { ideal: width },
//                    height: { ideal: height },
//                },
//                audio: false
//            })
//            .then((stream) => {
//                video.srcObject = stream;
//                video.play();
//            })
//            .catch((err) => {
//                console.error(`An error occurred: ${err}`);
//            });
//    }



//
//    function captureImage(target) {
//        // Get the actual dimensions of the video container
//        width = video.getBoundingClientRect().width;
//        height = video.getBoundingClientRect().height;
//
//        const context = canvas.getContext("2d");
//        canvas.width = width;
//        canvas.height = height;
//        context.drawImage(video, 0, 0, width, height);
//
//        const data = canvas.toDataURL("image/png");
//        target.setAttribute("src", data);
//    }
//
//    // Set up our event listener to run the startup process
//    // once loading is complete.
//    // window.addEventListener("load", startup, false);
//
//    window.addEventListener("load", () => {
//        document.getElementById("startButton").onclick = startup
//    }, false);
//
//    // console.log(window.location)
//    // var url = new URL(window.location);
//    // console.log(url)
//    // var id = url.searchParams.get("id");
//    // console.log(id)
//
//})();
