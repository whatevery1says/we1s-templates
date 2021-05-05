# README

The WE1S Query Builder is a web-based MongoDB query builder. You can use the builder's form to generate a MongoDB query string that can be pasted into other tools that perform MongoDB queries. This can often be a time saver because MongoDB's syntax can make it difficult to construct complex queries.

The Query Builder comes pre-configured with a list of fields drawn from the WE1S manifest schema v2.0. If these fields do not conform to your data, you can modify the configuration in `assets/config/schema.js`. Each field has the following properties:

- `id`: A reference id which should generally be the same as the label.
- `label`: The name of the field, which will appear in the form's dropdown.
- `type`: The data type of the field ('string', 'integer', 'boolean').
- `size`: The width of the field in pixels.

It is also possible to introduce validation rules, and there are a couple of examples in the pre-configured schema. For further information, about configuring form, see the documentation for [jQuery-QueryBuilder](https://querybuilder.js.org/index.html). Hint: If your metadata field is not pre-configured, you don't necessarily have to change the configuration. If you are doing a one-off operation, it may be simpler to choose another with the same data type, copy the generated field, and then replace your field's name for the one in the generated query.
