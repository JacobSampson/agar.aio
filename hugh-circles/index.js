const canvas = document.getElementById('canvas');

const largeParams = {
    'dp': 2,
    'minDist': 15,
    'param1': 100,
    'param2': 50,
    'minRadius': 10,
    'maxRadius': 0
}

const smallParams = {
    'dp': 1,
    'minDist': 5,
    'param1': 100,
    'param2': 4,
    'minRadius': 0,
    'maxRadius': 5
}

// let params = largeParams;
let params = smallParams;

const MAX_IMAGE_WIDTH = 750;

function loadScript(url, callback){
    var script = document.createElement("script")
    script.type = "text/javascript";

    script.onload = function(){
        callback();
    };

    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}

function initialize() {
    loadScript('https://docs.opencv.org/3.4.0/opencv.js', () => console.log('CV loaded'));

    for (const [key, value] of Object.entries(params)) {
        document.getElementById(key).value = value;
    }
}

initialize();

function toggleParams(field) {
    params = params === smallParams ? largeParams : smallParams;    
}

function setParam(field) {
    const value = field.value;
    const name = field.name;

    params[name] = Number.parseInt(value);
    console.log(params)
}

function convert(image) {
    console.log(params)

    // Load image from canvas
    const { width, height } = image;
    let src = cv.imread('canvas');

    // BW
    let dstBW = new cv.Mat()
    cv.cvtColor(src, dstBW, cv.COLOR_RGBA2GRAY, 0);
    cv.imshow("canvasBW", dstBW)

    // Resize
    let dstResized = new cv.Mat()

    const widthResized = Math.min(MAX_IMAGE_WIDTH, width);
    const heightResized = (widthResized / width) * height;

    dsize = new cv.Size(widthResized, heightResized)
    cv.resize(dstBW, dstResized, dsize, 0, 0, cv.INTER_AREA)

    cv.imshow("canvasResize", dstResized)

    // Blur
    let dstBlurred = new cv.Mat()
    let ksize = new cv.Size(3, 3);
    let anchor = new cv.Point(-1, -1);

    // You can try more different parameters
    cv.blur(dstResized, dstBlurred, ksize, anchor, cv.BORDER_DEFAULT);
    cv.convertScaleAbs(dstBlurred, dstBlurred, 0.7, 100);
    cv.threshold(dstBlurred, dstBlurred, 245, 255, cv.THRESH_BINARY&cv.THRESH_OTSU)

    // cv.boxFilter(src, dst, -1, ksize, anchor, true, cv.BORDER_DEFAULT)
    cv.imshow('canvasBlur', dstBlurred);

    // Hough Circles: https://docs.opencv.org/3.4/d3/de5/tutorial_js_houghcircles.html
    // https://answers.opencv.org/question/214448/i-try-to-detect-circle-in-real-time-webcam-using-houghcircles-from-opencv-javascript/

    const houghCircles = (params, src) => {
        let dst = cv.Mat.zeros(src.rows, src.cols, cv.CV_8U);
        let circles = new cv.Mat();
        let color = new cv.Scalar(255, 0, 0);    

        cv.HoughCircles(src, circles, cv.HOUGH_GRADIENT,
            params.dp, params.minDist, params.param1,
            params.param2, params.minRadius, params.maxRadius);

        const points = [];
        // draw circles
        for (let i = 0; i < circles.cols; ++i) {
            let x = circles.data32F[i * 3];
            let y = circles.data32F[i * 3 + 1];
            let radius = circles.data32F[i * 3 + 2];
            points.push([x, y, radius]);
        }

        return [dst, points];
    }

    const drawCircles = (circles, dst, color, plusRadus=0) => {
        for (let i = 0; i < circles.length; ++i) {    
            let [x,y,radius] = circles[i];
            let center = new cv.Point(x, y);
    
            cv.circle(dst, center, radius + plusRadus, color, -1);
        }
    }

    let [dst, parsedCircles] = houghCircles(smallParams, dstBlurred)
    console.log(parsedCircles)
    // cv.imshow('canvasOutputSmall', dst);
    drawCircles(parsedCircles, dstBlurred, new cv.Scalar(255, 255, 255), 5)

    cv.imshow('canvasOutputSmall', dstBlurred);

    [dst, parsedCircles] = houghCircles(largeParams, dstBlurred)
    console.log(parsedCircles);
    drawCircles(parsedCircles, dst, new cv.Scalar(255, 0, 0));

    // Find bombs
    parsedCircles.filter(([x, y, radius]) => {
        const originalWidth = Math.round(x * (width / widthResized));
        const originalHeight = Math.round(y * (height / heightResized));
        
        begin = originalWidth * src.cols * 3 + originalHeight * 3

        console.log(src.data[begin], src.data[begin + 1], src.data[begin + 2])
    });

    cv.imshow('canvasOutputLarge', dst);

    console.log('Done!');
    // src.delete() ; dst.delete(); circles.delete(); dstBW.delete(); dstResized.delete()
}

function grid(image) {
    // Load image from canvas
    let src = cv.imread('canvas');

    // Resize
    let dst = new cv.Mat()

    cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY, 0);

    const widthResized = 100;
    const heightResized = 100;

    dsize = new cv.Size(widthResized, heightResized)
    cv.resize(src, dst, dsize, 0, 0, cv.INTER_AREA)

    cv.imshow("canvasGrid", dst)
}

function displayImage(image) {
    console.log('Converting circles');
    const { width, height } = image;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0);

    return image;
}

const createImage = (fr) => {
    const image = new Image();
    image.onload = () => { displayImage(image); convert(image); }
    image.src = fr.result;
}    

function loadImage() {
    const input = document.getElementById('img');

    const file = input.files[0];
    const fr = new FileReader();
    fr.onload = () => createImage(fr);
    fr.readAsDataURL(file);
}
