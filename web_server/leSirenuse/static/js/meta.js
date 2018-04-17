// Dom Nodes

//var circle1 = document.querySelector('#js-circle1');
//var circle2 = document.querySelector('#js-circle2');
//var connector = document.querySelector('#js-connector');
//var VIEWBOX_SIZE = {
//    W: 1200,
//    H: 1200
//};
//var SIZES = {
//    CIRCLE1: 96,
//    CIRCLE2: 64,
//};


//let path = metaball(SIZES.CIRCLE1, SIZES.CIRCLE2, [400, 600], [600, 600]);
//connector.setAttribute('d', path);
function attachListeners(circle, start, end, center) {
    var circle1$ = rxjs.Observable.of([0, 0])
        .do(loc => {
            moveTo(loc, circle1);
        });

    var circle2$ = rxjs.Observable.interval(0, rxjs.Scheduler.animationFrame)
        .map(frame => 200 * Math.sin(frame / 500))
        .map(x => [600 + x, 600])
        .do(loc => {
            moveTo(loc, circle2);
        });

    rxjs.Observable
        .combineLatest(circle1$, circle2$, (circle1Loc, circle2Loc) =>
            metaball(SIZES.CIRCLE1, SIZES.CIRCLE2, circle1Loc, circle2Loc),
        )
        .subscribe(path => {
            connector.setAttribute('d', path);
        });
}

/**
 * Based on Metaball script by SATO Hiroyuki
 * http://shspage.com/aijs/en/#metaball
 */
function metaball(radius1, radius2, center1, center2, handleSize = 2.4, v = 0.5) {
    var HALF_PI = Math.PI / 2;
    var d = dist(center1, center2);
    var maxDist = radius1 + radius2 * 2.5;
    let u1, u2;

    if (radius1 === 0 || radius2 === 0 || d > maxDist || d <= Math.abs(radius1 - radius2)) {
        return '';
    }

    if (d < radius1 + radius2) {
        u1 = Math.acos(
            (radius1 * radius1 + d * d - radius2 * radius2) / (2 * radius1 * d),
        );
        u2 = Math.acos(
            (radius2 * radius2 + d * d - radius1 * radius1) / (2 * radius2 * d),
        );
    } else {
        u1 = 0;
        u2 = 0;
    }

    // All the angles
    var angleBetweenCenters = angle(center2, center1);
    var maxSpread = Math.acos((radius1 - radius2) / d);

    var angle1 = angleBetweenCenters + u1 + (maxSpread - u1) * v;
    var angle2 = angleBetweenCenters - u1 - (maxSpread - u1) * v;
    var angle3 = angleBetweenCenters + Math.PI - u2 - (Math.PI - u2 - maxSpread) * v;
    var angle4 = angleBetweenCenters - Math.PI + u2 + (Math.PI - u2 - maxSpread) * v;
    // Points
    var p1 = getVector(center1, angle1, radius1);
    var p2 = getVector(center1, angle2, radius1);
    var p3 = getVector(center2, angle3, radius2);
    var p4 = getVector(center2, angle4, radius2);

    // Define handle length by the
    // distance between both ends of the curve
    var totalRadius = radius1 + radius2;
    var d2Base = Math.min(v * handleSize, dist(p1, p3) / totalRadius);

    // Take into account when circles are overlapping
    var d2 = d2Base * Math.min(1, d * 2 / (radius1 + radius2));

    var r1 = radius1 * d2;
    var r2 = radius2 * d2;

    var h1 = getVector(p1, angle1 - HALF_PI, r1);
    var h2 = getVector(p2, angle2 + HALF_PI, r1);
    var h3 = getVector(p3, angle3 + HALF_PI, r2);
    var h4 = getVector(p4, angle4 - HALF_PI, r2);

    return metaballToPath(
        p1, p2, p3, p4,
        h1, h2, h3, h4,
        d > radius1,
        radius2,
    );
}

function metaballToPath(p1, p2, p3, p4, h1, h2, h3, h4, escaped, r) {
    return [
    'M', p1,
    'C', h1, h3, p3,
    'A', r, r, 0, escaped ? 1 : 0, 0, p4,
    'C', h4, h2, p2,
  ].join(' ');
}


/**
 * Utils
 */
function moveTo([x, y] = [0, 0], element) {
    element.setAttribute('cx', x);
    element.setAttribute('cy', y);
}

function line([x1, y1] = [0, 0], [x2, y2] = [0, 0], element) {
    element.setAttribute('x1', x1);
    element.setAttribute('y1', y1);
    element.setAttribute('x2', x2);
    element.setAttribute('y2', y2);
}

function dist([x1, y1], [x2, y2]) {
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5;
}

function angle([x1, y1], [x2, y2]) {
    return Math.atan2(y1 - y2, x1 - x2);
}

function getVector([cx, cy], a, r) {
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}
