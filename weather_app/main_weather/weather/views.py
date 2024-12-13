from django.shortcuts import render
from .forms import CityForm
import requests

def index(request):
    # OpenWeatherMap API setup
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=8dd3512f8ccf616e9bd1071a679dcb97'

    # Unsplash API setup
    unsplash_url = 'https://api.unsplash.com/search/photos?query={}&client_id=WPHnaQQyvJUyYXjTHu-XrTMEU7vxUGmSLEVJrWgROxM'

    # Check if there's a session for cities, otherwise initialize it
    if 'cities' not in request.session:
        request.session['cities'] = ['Las Vegas']  # Default city if none are provided

    # Initialize form
    form = CityForm(request.POST or None)

    # Add a new city if form is valid
    if form.is_valid():
        new_city = form.cleaned_data['city']
        if new_city and new_city not in request.session['cities']:
            request.session['cities'].append(new_city)
            request.session.modified = True  # Indicate that session data has changed

    # Remove a city if request is made to delete it
    if request.method == "POST" and "remove_city" in request.POST:
        city_to_remove = request.POST.get("remove_city")
        if city_to_remove in request.session['cities']:
            request.session['cities'].remove(city_to_remove)
            request.session.modified = True  # Indicate that session data has changed

    weather_data = []

    for city in request.session['cities']:
        # Fetch weather data
        city_weather = requests.get(weather_url.format(city)).json()

        # Default weather dictionary
        weather = {
            'city': city,
            'temperature': 'N/A',
            'description': 'N/A',
            'icon': '01d',  # Default to clear sky icon
            'image_url': '/static/default_background.jpg',  # Default background image
        }

        if city_weather.get('cod') == 200:  # Check if the city was found
            weather.update({
                'temperature': city_weather['main']['temp'],
                'description': city_weather['weather'][0]['description'],
                'icon': city_weather['weather'][0]['icon']
            })

            # Fetch city background image from Unsplash
            unsplash_response = requests.get(unsplash_url.format(city)).json()
            if unsplash_response.get('results'):
                weather['image_url'] = unsplash_response['results'][0]['urls']['regular']

        weather_data.append(weather)

    context = {
        'weather_data': weather_data,
        'form': form  # Pass form to the template
    }

    return render(request, 'weather/index.html', context)
