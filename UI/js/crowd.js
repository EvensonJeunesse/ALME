// ------
// Colors
// ------

var shirtColors = ['43875e', '03aa96', 'e85140', 'cbaa74', 'f78b1f', 'd5d4d2', '01a451', 'da2c47', '615ea3', '5f5ea0', 'e77e9c', '14afcd', 'dfb217', '444547', '8e60a8', '8b8d8a', '0093d2', 'f39079'];
var skinColors = ['755d5b', 'ca6c62', 'ed917c', 'dab5af', 'c66c63'];
var pantsColors = ['0293d2', '444547', '8b60a7', '74a1b4', '6f6f6f', '00a996', 'd1aa73', '416c51'];
var hairColors = ['804c3e', 'a16938', '454648', 'ceab75', '333736'];
var shoeColors = ['bebab9', '414745', '006ead', 'a37953', 'dadbdd', '646569', '8c8c8a', 'e54e5f'];
var backpackColors = ['63bf8c', 'e74f5c', '454648'];

// ----------------
// Helper functions
// ----------------

function getRandomArrayValue(array) {
  var randomIndex = Math.floor(Math.random() * (array.length));
  return array[randomIndex]
}

function getRandomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

// -------
// Aliases
// -------

let Application = PIXI.Application;
let loader = PIXI.Loader.shared;
let resources = PIXI.Loader.shared.resources;
let Sprite = PIXI.Sprite;
let TextureCache = PIXI.utils.TextureCache;
let Rectangle = PIXI.Rectangle;
let Container = PIXI.Container;

// -----
// Stage
// -----

let siteWidth = document.body.clientWidth;
let siteHeight = document.body.clientHeight;
let spriteWidth = 50;
let spriteHeight = 50;
let app = new Application({
  width: siteWidth,
  height: siteHeight,
  resolution: window.devicePixelRatio,
  autoDensity: true,
  backgroundColor: 0xf0e7da
});

window.addEventListener('resize', resize);

function resize() {
  siteWidth = document.body.clientWidth;
  siteHeight = document.body.clientHeight;
  app.renderer.resize(siteWidth, siteHeight);
}

$("#app").append(app.view);

// -------------
// Init Textures
// -------------

loader
  .add('https://s3-us-west-2.amazonaws.com/s.cdpn.io/49240/sprites.json')
  .load(setup);

let people = [];

// -----
// Setup
// -----

function setup() {
  const groupSize = size;

  for (let i = 0; i < groupSize; i++) {
    people.push(new Person());
    people[i].generateSprite();
    const sprite = people[i].body.container;
    sprite.x = Math.random() * document.body.clientWidth;
    sprite.y = Math.random() * document.body.clientHeight;

    app.stage.addChild(sprite);
  }

  requestAnimationFrame(loop);
}

// ----
// Loop
// ----

function loop() {
  for (let i = 0; i < people.length; i++) {

    // aliases
    const person = people[i];
    const sprite = person.body.container;

    // update simulation
    person.velocity.add(person.acceleration);
    person.velocity.limit(person.maxSpeed);
    person.position.add(person.velocity);
    person.x = person.position.x;
    person.y = person.position.y;
    person.acceleration.multiply({x: 0, y: 0});
    person.boundaries();
    person.animateScale();

    // translate simulation values to sprite
    sprite.x = person.position.x;
    sprite.y = person.position.y;
    sprite.rotation = person.velocity.angle() + 1.5708; // Adjust the sprite to face the correct direction
    person.body.armLeft.container.height = person.scale;
    person.body.armRight.container.height = person.scale * -1;
    person.body.legLeft.container.height = person.scale * -1;
    person.body.legRight.container.height = person.scale;
  }

  requestAnimationFrame(loop);
}

// ------
// Person
// ------

class Person {
  constructor() {
    this.position = new Victor(Math.random() * siteWidth, Math.random() * siteHeight);
    this.velocity = new Victor(Math.random() * (1 - 0.7) + 0.7, Math.random() * (1 - 0.7) + 0.7);
    this.acceleration = new Victor(0, 0);
    this.maxSpeed = 10;
    this.maxForce = 0.01;
    this.scale = spriteHeight;
    this.scalingUp = false;
    this.shirtColor = `0x${getRandomArrayValue(shirtColors)}`;
    this.skinColor = `0x${getRandomArrayValue(skinColors)}`;
    this.pantsColor = `0x${getRandomArrayValue(pantsColors)}`;
    this.hairColor = `0x${getRandomArrayValue(hairColors)}`;
    this.shoeColor = `0x${getRandomArrayValue(shoeColors)}`;
    this.backpackColor = `0x${getRandomArrayValue(backpackColors)}`;
    this.body = {
      container: null,
      torso: null,
      head: null,
      armLeft: {
        container: null,
        arm: null,
        hand: null
      },
      armRight: {
        container: null,
        arm: null,
        hand: null
      },
      legLeft: {
        container: null,
        leg: null,
        foot: null
      },
      legRight: {
        container: null,
        leg: null,
        foot: null
      }
    }

    var velocityRotation = Math.random() * 4;
    this.velocity.rotate(velocityRotation);
  }

  generateSprite() {
    let id = resources['https://s3-us-west-2.amazonaws.com/s.cdpn.io/49240/sprites.json'].textures;
    let backpack = getRandomNumber(0, 1);

    this.body.container = new Container();
    this.body.armLeft.container = new Container();
    this.body.armRight.container = new Container();
    this.body.legLeft.container = new Container();
    this.body.legRight.container = new Container();

    this.body.torso = new Sprite(id['torso.png']);
    this.body.torso.anchor.set(0.5, 0.5);
    this.body.torso.tint = this.shirtColor;

    this.body.head = new Sprite(id[`head-${getRandomNumber(1, 5)}.png`]);
    this.body.head.anchor.set(0.5, 0.5);
    this.body.head.tint = this.hairColor;

    if (backpack) {
      this.body.backpack = new Sprite(id['backpack.png']);
      this.body.backpack.anchor.set(0.5, 0.5);
      this.body.backpack.position.set(0, 18);
      this.body.backpack.tint = this.backpackColor;
    }

    this.body.armLeft.arm = new Sprite(id['arm.png']);
    this.body.armLeft.arm.anchor.set(0.5, 1);
    this.body.armLeft.arm.tint = this.shirtColor;

    this.body.armLeft.hand = new Sprite(id['hand.png']);
    this.body.armLeft.hand.position.set(0, -68);
    this.body.armLeft.hand.anchor.set(0.5, 1);
    this.body.armLeft.hand.tint = this.skinColor;

    this.body.armRight.arm = new Sprite(id['arm.png']);
    this.body.armRight.arm.anchor.set(0.5, 1);
    this.body.armRight.arm.tint = this.shirtColor;

    this.body.armRight.hand = new Sprite(id['hand.png']);
    this.body.armRight.hand.scale.x = -1;
    this.body.armRight.hand.position.set(0, -68);
    this.body.armRight.hand.anchor.set(0.5, 1);
    this.body.armRight.hand.tint = this.skinColor;

    this.body.legLeft.leg = new Sprite(id['leg.png']);
    this.body.legLeft.leg.anchor.set(0.5, 1);
    this.body.legLeft.leg.tint = this.pantsColor;

    this.body.legLeft.foot = new Sprite(id['foot.png']);
    this.body.legLeft.foot.position.set(0, -60);
    this.body.legLeft.foot.anchor.set(0.5, 0.5);
    this.body.legLeft.foot.tint = this.shoeColor;

    this.body.legRight.leg = new Sprite(id['leg.png']);
    this.body.legRight.leg.scale.x = -1;
    this.body.legRight.leg.anchor.set(0.5, 1);
    this.body.legRight.leg.tint = this.pantsColor;

    this.body.legRight.foot = new Sprite(id['foot.png']);
    this.body.legRight.foot.scale.x = -1;
    this.body.legRight.foot.position.set(0, -60);
    this.body.legRight.foot.anchor.set(0.5, 0.5);
    this.body.legRight.foot.tint = this.shoeColor;

    this.body.armLeft.container.addChild(this.body.armLeft.hand);
    this.body.armLeft.container.addChild(this.body.armLeft.arm);
    this.body.armLeft.container.position.set(-48, 0);

    this.body.armRight.container.addChild(this.body.armRight.hand);
    this.body.armRight.container.addChild(this.body.armRight.arm);
    this.body.armRight.container.position.set(48, 0);

    this.body.legLeft.container.addChild(this.body.legLeft.foot);
    this.body.legLeft.container.addChild(this.body.legLeft.leg);
    this.body.legLeft.container.position.set(-30, 0);

    this.body.legRight.container.addChild(this.body.legRight.foot);
    this.body.legRight.container.addChild(this.body.legRight.leg);
    this.body.legRight.container.position.set(30, 0);

    this.body.container.addChild(this.body.legLeft.container);
    this.body.container.addChild(this.body.legRight.container);
    this.body.container.addChild(this.body.armLeft.container);
    this.body.container.addChild(this.body.armRight.container);
    this.body.container.addChild(this.body.torso);
    if (backpack) this.body.container.addChild(this.body.backpack);
    this.body.container.addChild(this.body.head);
    this.body.container.position.set(100, 100);
    this.body.container.scale.set(0.2, 0.2);
  }

  boundaries() {
    let d = 60;
    let desired = null;

    if (this.position.x < d) {
      desired = new Victor(this.maxSpeed, this.velocity.y);
    } else if (this.position.x > siteWidth - d) {
      desired = new Victor(-this.maxSpeed, this.velocity.y);
    }

    if (this.position.y < d) {
      desired = new Victor(this.velocity.x, this.maxSpeed);
    } else if (this.position.y > siteHeight - d) {
      desired = new Victor(this.velocity.x, -this.maxSpeed);
    }

    if (desired !== null) {
      desired.normalize();
      desired.multiply({x: this.maxSpeed, y: this.maxSpeed});

      var steer = desired.subtract(this.velocity);
          steer.limit(this.maxForce, this.maxForce);

      this.applyForce(steer);
    }
  }

  applyForce(force) {
    this.acceleration.add(force);
  }

  animateScale() {
    const scaleSpeed = this.velocity.length() * 3;
    const minSize = -70;
    const maxSize = 70;

    if (this.scalingUp === true) {
      if (this.scale <= maxSize) {
        this.scale += scaleSpeed
      } else {
        this.scalingUp = false;
        this.scale = maxSize;
      }
    } else {
      if (this.scale >= minSize) {
        this.scale -= scaleSpeed
      } else {
        this.scalingUp = true;
        this.scale = minSize;
      }
    }
  }
}
