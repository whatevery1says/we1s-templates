var schema = [
    {
      'id': 'contributors',
      'label': 'contributors',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'content',
      'label': 'content',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'created',
      'label': 'created',
      'type': 'date',
      'validation': {
        'callback': function (value, rule) {
          var d = moment(value, 'YYYY-MM-DD', true).isValid()
          var dt = moment(value, 'YYYY-MM-DDTHH:mm:ss', true).isValid()
          if (d === true || dt === true) {
            return true
          } else {
            return ['<code>{0}</code> is not a valid date format. Please use <code>YYYY-MM-DD</code> or <code>YYYY-MM-DDTHH:mm:ss</code>.', value]
          }
        }
      }
    },
    {
      'id': 'description',
      'label': 'description',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'documentType',
      'label': 'documentType',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'encoding',
      'label': 'encoding',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'format',
      'label': 'format',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'id',
      'label': 'id',
      'type': 'string',
      'size': 30
    },
    {
      'id': '_id',
      'label': '_id',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'image',
      'label': 'image',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'keywords',
      'label': 'keywords',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'label',
      'label': 'label',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'metapath',
      'label': 'metapath',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'mediatype',
      'label': 'mediatype',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'name',
      'label': 'name',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'namespace',
      'label': 'namespace',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'licenses',
      'label': 'licenses',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'notes',
      'label': 'notes',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'OCR',
      'label': 'OCR',
      'type': 'boolean',
      'size': 30,
      'input': 'radio',
      'values': [true, false],
      'operators': ['equal', 'not_equal']
    },
    {
      'id': 'processes',
      'label': 'processes',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'publisher',
      'label': 'publisher',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'queryterms',
      'label': 'queryterms',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'relationships',
      'label': 'relationships',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'rights',
      'label': 'rights',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'shortTitle',
      'label': 'shortTitle',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'sources',
      'label': 'sources',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'title',
      'label': 'title',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'updated',
      'label': 'updated',
      'type': 'date',
      'validation': {
        'callback': function (value, rule) {
          var d = moment(value, 'YYYY-MM-DD', true).isValid()
          var dt = moment(value, 'YYYY-MM-DDTHH:mm:ss', true).isValid()
          if (d === true || dt === true) {
            return true
          } else {
            return ['<code>{0}</code> is not a valid date format. Please use <code>YYYY-MM-DD</code> or <code>YYYY-MM-DDTHH:mm:ss</code>.', value]
          }
        }
      }
    },
    {
      'id': 'version',
      'label': 'version',
      'type': 'string',
      'size': 30
    },
    {
      'id': 'workstation',
      'label': 'workstation',
      'type': 'string',
      'size': 30
    }
  ]
