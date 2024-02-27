## ADD LANGUAGE TO SEETINGS.PY 
```python
    LANGUAGES = [
        ("ru", "Russian"),
        ("en", "English"),
        ("es", "Spanish"),
        ("de", "German"),
        ('uz', "Uzbek"),
        ("pt", "Partuguese"),

    ]
 ```

 ## add {% translate 'some_text' %}
 ## python manage.py makemessages -l language_code to generate .po file
 ## after translate po file run
 ```sh 
 python manage.py compilemessages
 ```