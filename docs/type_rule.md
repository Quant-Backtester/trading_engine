
## Use enum when:
- The value represents a closed, semantic state
- Invalid values must be rejected early
- The value may be persisted, logged, or exchanged
- You want runtime safety

## Use type (type alias / Literal) when:
- The value is a label or tag
- Errors can be caught at type-check time only
- You want zero runtime overhead
- The value is internal and short-lived




## Duck Typing
- prefer duck typing over inheritance, as inheritance will add runtime overhead
- Try to avoid inheritance if you are not using the `super()` function call