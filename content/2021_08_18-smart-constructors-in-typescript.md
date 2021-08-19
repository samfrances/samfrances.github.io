"Smart constructors" in Typescript
Date: 2021-08-19 16:00
UniqueId: 2021-04-3-smart-constructors-in-typescript-f3f37b4f-a33b-4b1b-b072-e4471e5cc686
Modified: 2021-08-19 16:00
Category: Blog
Tags: typescript, types
Slug: smart-constructors-in-typescript
Authors:
Summary: A useful pattern for constrained types

I want to share a small but very useful pattern which I discovered on the pages
of two highly recommended books:

* [Programming with Types](https://www.manning.com/books/programming-with-types) by [Vlad Riscutia](https://vladris.com/)
* [Domain Modelling Made Functional](https://pragprog.com/titles/swdddf/domain-modeling-made-functional/) by [Scott Wlaschin](https://fsharpforfunandprofit.com/)

In functional languages this pattern generally gets called "smart constructors", and it is the partial fulfilment of a wish that I have had for some time:

> I wish the type system could enforce more interesting constraints than "this must be a string" or "this must be a number", like "this must be a number between 1 and 5" or "this string must be a valid email address".

### A motivating example

At [Cydar](https://www.cydarmedical.com/), we use a distributed content-addressable storage system we call "The Disthashbin", which lets you store and access files using their sha256 hash - or as we say around here, its "hashbin ref".

Here's a very simplified outline of the client interface.

```
:::typescript

class HashbinClient {

  get_blob(ref: string) {
    console.log(`Getting blob: ${ref}`);
  }

}
```

You use it as follows:

```
:::typescript

const hb = new HashbinClient();

const validRef = "beefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeef";

hb.get_blob(validRef);
```
In reality it would return some sort of Blob object with the content of the file, but you get the idea.

An obvious issue with this code is that it will just as happily accept a string which is not a valid sha256 hash. The following will compile just fine:

```
:::typescript

const badRef = "this is not a valid sha256 hash";

hb.get_blob(badRef);
```

### A validation function

If you're anything like me, your first instinct is to write a function like this:

```
:::typescript

function validateRef(ref: string) {
  const sha256regex = /^[A-Fa-f0-9]{64}$/
  if (!sha256regex.test(ref)) {
    throw new Error(`Invalid ref: ${ref}`);
  }
}

class HashbinClient {

  get_blob(ref: string) {
    validateRef(ref);
    console.log(`Getting blob: ${ref}`);
  }

}
```

However, now if we extend the API of the `HashbinClient` class, we have to remember to use the `validateRef` function in every public method that accepts a hashbin ref.

```
:::typescript

class HashbinClient {

  get_blob(ref: string) {
    validateRef(ref);
    console.log(`Getting blob: ${ref}`);
  }

  get_file(ref: string) {
    validateRef(ref);
    console.log(`Getting file: ${ref}`);
  }

  exists(ref: string) {
    validateRef(ref);
    console.log(`Checking if ref exists: ${ref}`);
  }

  del(ref: string) {
    validateRef(ref);
    console.log(`Deleting: ${ref}`);
  }

}
```

We are also faced with a dilemma when it comes to helper methods. Should a helper method assume that the ref has already been validated at in the API method that calls it, or should it revalidate?

```
:::typescript

class HashbinClient {

  get_blob(ref: string) {
    validateRef(ref);
    console.log(`Getting blob: ${ref}`);
    helper(ref);
  }

  private helper(ref: string) {
    // validateRef(ref)   // Yay or nay?
    console.log("Do I revalidate or don't I?")
  }

}
```

Ultimately the only way to be sure is to check every caller of the helper function, or if that caller itself receives a ref, each of the caller's callers, and so on.

Eventually, you (or another developer who is less familiar with the codebase) will forget to validate a ref in the right place, and you'll end up with an invalid hashbin ref somewhere deeper in your call stack.

### A smart constructor

The first step towards a better solution is to stop thinking in terms of "strings which are valid hashbin refs", and instead think of hashbin refs as their own type. In other words, we need to get over our [primitive obsession](https://refactoring.guru/smells/primitive-obsession).

We move our validation code into the `Ref` constructor, making it impossible to create an invalid hashbin ref.

```
#!typescript
// ref.ts

const sha256regex= /^[A-Fa-f0-9]{64}$/

export default class Ref {
  value: string;
  constructor(value: string) {
    if (!sha256regex.test(value)) {
      throw new Error(`Invalid ref: ${value}`);
    }
    this.value = value;
  }
}

```
We then update our `HashbinClient` accordingly.

```
:::typescript

class HashbinClient {

  get_blob(ref: Ref) {
    console.log(`Getting blob: ${ref.value}`);
  }

  get_file(ref: Ref) {
    console.log(`Getting file: ${ref.value}`);
  }

  exists(ref: Ref) {
    console.log(`Checking if ref exists: ${ref.value}`);
  }

  del(ref: Ref) {
    console.log(`Deleting: ${ref.value}`);
  }

```

This falls short of the dream of enforcing validity in the type-system itself, but it does use a combination of type-checking and runtime validation to ensure that you can never encounter an invalid hashbin ref.

In other words, if you have a function (method, class etc.) which requires a `Ref` instance, you can be sure that the body of that function will never run with an invalid hashbin ref, because to do that you would have to first create an invalid hashbin ref to pass to the function, and we've made that impossible.

```
:::typescript

const validRefString = "beefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeef";

const badRefString = "this is not a valid hashbin ref";

// This runs fine
hb.get_file(new Ref(validRefString));

// This throws an error *before* get_file() has a chance to run
hb.get_file(new Ref(badRefString));

// This won't compile
hb.get_blob(badRefString);
```

### Making sure values stay valid

You've probably already spotted a flaw in the code above, for although we have prevented you from creating an invalid hashbin ref, you can take a valid ref and then make it invalid.

```
const validRef = new Ref(validRefString);
validRef.value = badRefString;
```
In functional languages, this wouldn't be an issue, since data structures are generally immutable by default. But this is easy to fix with Typescript's `readonly` modifier.

```
:::typescript
export default class Ref {
  readonly value: string;
  constructor(value: string) {
    if (!sha256regex.test(value)) {
      throw new Error(`Invalid ref: ${value}`);
    }
    this.value = value;
  }
}
```

### Structural typing gotchas

Typescript's structural type system also presents another escape hatch. This is because the type checker isn't checking whether items passed to a `Ref` parameter are instances of the `Ref` class. It only checks if they have the same structure as an instance of the `Ref` class, which in this case just means having a field called `value` which stores a `string`.

```
:::typescript
// This compiles
const sneakyRef: Ref = { value: "not a valid ref" }
```

To get around this, we have to use a neat trick with `unique symbol` to simulate nominal typing.

```
#!typescript

// ref.ts

const sha256regex= /^[A-Fa-f0-9]{64}$/;

declare const RefType: unique symbol;

export default class Ref {
  [RefType]: void;
  readonly value: string;
  constructor(value: string) {
    if (!sha256regex.test(value)) {
      throw new Error(`Invalid ref: ${value}`);
    }
    this.value = value;
  }
}
```

This `unique symbol` type is private to the `ref` module. As long as we don't export it, nothing outside of the `ref` module can create something using that symbol.

Now, the following will not compile:

```
:::typescript
// This won't compile any more
const sneakyRef: Ref = { value: "not a valid ref" };
```

The great thing about this technique is that it only applies at the type level. If you look at the generated JavaScript code, the `[RefType]` field is removed.

```
:::javascript
const sha256regex = /^[A-Fa-f0-9]{64}$/;
export default class Ref {
    constructor(value) {
        if (!sha256regex.test(value)) {
            throw new Error(`Invalid ref: ${value}`);
        }
        this.value = value;
    }
}
```

This means that if you need to use instances of `Ref` in contexts where you only want to use serializable values (e.g. as part of [redux](https://redux.js.org/) state), this won't present an issue.

### Private constructor

Another way to get around our smart constructor is to create a subclass of `Ref` that will nullify our validation.

```
:::typescript

const validRefString = "beefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeef";

export default class SneakyRefSubclass extends Ref {
  value: string;
  constructor(value: string) {
    super(validRefString);
    this.value = value;
  }
}
```
Any parameter which requires a `Ref` will also accept an instance of a subclass of `Ref`.

```
:::typescript
// Disaster!

// This runs without raising an error
const sneakyRef = new SneakyRefSubclass("bad ref");

// And this compiles!
hb.get_file(sneakyRef);
```

To stop this from happening, we have to forbid subclassing of `Ref`. At the time of writing, Typescript doesn't have a `final` modifier, so you can't do this:

```
:::typescript
final class Ref {
    // etc.
}
```

What you can do is make the constructor private, which prevents subclassing, and also stops code outside of the class from creating an instance using `new`.

```
:::typescript

export default class Ref {
  [RefType]: void;
  readonly value: string;
  private constructor(value: string) {
    if (!sha256regex.test(value)) {
      throw new Error(`Invalid ref: ${value}`);
    }
    this.value = value;
  }

  // This is how we create instances now
  static create(value: string) {
    return new Ref(value);
  }
}

```
Now our `SneakyRefSubclass` will no longer compile.

### Complete example

Here's the complete example, with a bit of tidying up here and there.

```
#!typescript
// ref.ts

const sha256regex= /^[A-Fa-f0-9]{64}$/;

declare const RefType: unique symbol;

class Ref {
  [RefType]: void;
  readonly value: string;
  private constructor(value: string) {
    if (!sha256regex.test(value)) {
      throw new Error(`Invalid ref: ${value}`);
    }
    this.value = value;
  }

  static create(value: string) {
    return new Ref(value);
  }
}

// Only export the type, since clients of this module
// don't need access to the runtime class
export type { Ref };

// No need to reveal externally that we're using a class,
// So export a factory function
export default function create(value: string) {
  return Ref.create(value)
}

```

```
#!typescript
// hashbin-client.ts

import type { Ref } from "./ref";

export default class HashbinClient {

  get_blob(ref: Ref) {
    console.log(`Getting blob: ${ref.value}`);
  }

  get_file(ref: Ref) {
    console.log(`Getting file: ${ref.value}`);
  }

  exists(ref: Ref) {
    console.log(`Checking if ref exists: ${ref.value}`);
  }

  del(ref: Ref) {
    console.log(`Deleting: ${ref.value}`);
  }

}
```

```
#!typescript
// index.ts

import createRef from "./ref"
import HashbinClient from "./hashbin-client";

const hb = new HashbinClient();

const validRefString = "beefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeefbeef";

const badRefString = "this is not a valid hashbin ref"

hb.get_file(createRef(validRefString));

// Throws an error
hb.get_file(createRef(badRefString));
```

### Conclusion: Why care?

Ultimately, this pattern reduces the burden of validation by removing the dilemma of where and when to run the validation function. You run validation code when creating a value, and from that point onwards you can trust that you have a valid item. That alone is worth the price of having to wrap your primitive values.

But the truth is, you should probably be wrapping your primitive values anyway. Conceptually, a string is rarely a string, but a name, an email address, a uuid etc.; an integer is rarely an integer - rather it's a temperature, a timestamp, a width, an age etc.

NASA found this out to their peril in 1999.

> The Mars Climate Orbiter crashed and disintegrated in the Mars atmosphere because a component developed by Lockheed provided momentum measured in pound-force seconds, while another component developed by NASA expected momentum as Newton seconds. *-- [Vlad Riscutia](https://vladris.com/blog/2018/09/09/clean-code-types.html)*

Who knows? Maybe this disaster could have been averted by function parameters which accepted `NewtonSeconds` or `PoundForceSeconds` rather than `int`.

I also want to emphasize that smart constructors are not the only way to enforce complex constraints using the type system.

Take the related example of validating a hex colour. You could use a smart constructor very similar to `Ref`, or you could do something like the following (warning: Not the most efficient way to store hex colours!):

```
type HexDigit = "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9"|"a"|"b"|"c"|"d"|"e"|"f";

type HexColor = [HexDigit, HexDigit, HexDigit, HexDigit, HexDigit, HexDigit];

const red: HexColor = ["f", "f", "0", "0", "0", "0"];

const wont_compile: HexColor = ["f", "f", "0", "@", "0", "0"];

const wont_compile_either: HexColor = ["f", "f"];
```

How far these approaches will take you, and under what circumstances, is a discussion for another day.

### Further reading

* Articles
    - [Designing with types: Single case union types](https://fsharpforfunandprofit.com/posts/designing-with-types-single-case-dus/) by [Scott Wlaschin](https://fsharpforfunandprofit.com/)
    - [The Integrity of Simple Values](https://medium.com/pragmatic-programmers/the-integrity-of-simple-v-alues-1fbbd2e7f4a8) by [Scott Wlaschin](https://fsharpforfunandprofit.com/)
    - [Clean Code: Types](https://vladris.com/blog/2018/09/09/clean-code-types.html) by [Vlad Riscutia](https://vladris.com/)
* Books
    - [Programming with Types](https://www.manning.com/books/programming-with-types) by [Vlad Riscutia](https://vladris.com/)
    - [Domain Modelling Made Functional](https://pragprog.com/titles/swdddf/domain-modeling-made-functional/) by [Scott Wlaschin](https://fsharpforfunandprofit.com/)
