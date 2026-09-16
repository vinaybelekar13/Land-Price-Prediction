let map;
let marker;


/* =========================================
   INITIALIZE MAP
========================================= */

map = L.map("map").setView(
    [12.9716, 77.5946],
    11
);


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution:
            '&copy; OpenStreetMap contributors'
    }
).addTo(map);


/* =========================================
   LOCATION SELECT
========================================= */

document
    .getElementById("location")
    .addEventListener(
        "change",
        updateLocation
    );


async function updateLocation() {

    const location =
        document.getElementById("location").value;

    if (!location) {
        return;
    }

    try {

        const response =
            await fetch(
                "/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        location: location,

                        bhk: 2,

                        total_sqft: 1200,

                        bath: 2,

                        balcony: 1

                    })
                }
            );

        const data =
            await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        moveMarker(
            data.latitude,
            data.longitude
        );

    } catch (error) {

        console.error(error);

    }
}


/* =========================================
   MOVE MARKER
========================================= */

function moveMarker(lat, lon) {

    if (marker) {

        marker.setLatLng(
            [lat, lon]
        );

    } else {

        marker = L.marker(
            [lat, lon],
            {
                draggable: true
            }
        ).addTo(map);


        marker.on(
            "dragend",
            snapMarker
        );
    }

    map.setView(
        [lat, lon],
        14
    );

    document
        .getElementById("lat")
        .innerText =
            lat.toFixed(6);

    document
        .getElementById("lon")
        .innerText =
            lon.toFixed(6);
}


/* =========================================
   SNAP DRAGGED MARKER
========================================= */

async function snapMarker() {

    const position =
        marker.getLatLng();

    const location =
        document.getElementById(
            "location"
        ).value;

    /*
       We keep the model tied to the selected
       validated locality.

       The marker can be dragged visually,
       but prediction uses the selected
       validated locality.
    */

    moveMarker(
        position.lat,
        position.lng
    );
}


/* =========================================
   PREDICT
========================================= */

async function predictPrice() {

    const location =
        document.getElementById(
            "location"
        ).value;

    const bhk =
        document.getElementById(
            "bhk"
        ).value;

    const total_sqft =
        document.getElementById(
            "total_sqft"
        ).value;

    const bath =
        document.getElementById(
            "bath"
        ).value;

    const balcony =
        document.getElementById(
            "balcony"
        ).value;


    if (!location) {

        alert(
            "Please select a Bengaluru locality."
        );

        return;
    }


    const resultBox =
        document.getElementById(
            "result"
        );

    resultBox.innerHTML = `
        <div class="placeholder">
            <div class="big-icon">⏳</div>
            <p>Calculating prediction...</p>
        </div>
    `;


    try {

        const response =
            await fetch(
                "/predict",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        location:
                            location,

                        bhk:
                            bhk,

                        total_sqft:
                            total_sqft,

                        bath:
                            bath,

                        balcony:
                            balcony

                    })

                }
            );


        const data =
            await response.json();


        if (data.error) {

            resultBox.innerHTML = `
                <p>${data.error}</p>
            `;

            return;
        }


        /* Move map */

        moveMarker(
            data.latitude,
            data.longitude
        );


        /* Display result */

        resultBox.innerHTML = `

            <div class="price-box">

                <div class="price-label">
                    Estimated Property Price
                </div>

                <div class="price">
                    ₹ ${data.predicted_price}
                    Lakh
                </div>

            </div>


            <div class="location-name">

                📍 ${data.location}

            </div>


            <h3 style="margin-bottom:12px;">
                Nearby Amenities
            </h3>


            <div class="amenity-grid">

                ${amenityHTML(
                    "🏫",
                    "School",
                    data.amenities.School
                )}

                ${amenityHTML(
                    "🏥",
                    "Hospital",
                    data.amenities.Hospital
                )}

                ${amenityHTML(
                    "🎓",
                    "College",
                    data.amenities.College
                )}

                ${amenityHTML(
                    "🚌",
                    "Bus Stop",
                    data.amenities["Bus Stop"]
                )}

                ${amenityHTML(
                    "🚆",
                    "Railway",
                    data.amenities["Railway Station"]
                )}

                ${amenityHTML(
                    "🛒",
                    "Shopping",
                    data.amenities.Shopping
                )}

                ${amenityHTML(
                    "🏦",
                    "Bank",
                    data.amenities.Bank
                )}

                ${amenityHTML(
                    "🌳",
                    "Park",
                    data.amenities.Park
                )}

            </div>

        `;

    }

    catch (error) {

        console.error(error);

        resultBox.innerHTML = `
            <p>
                Something went wrong.
                Check the Flask terminal.
            </p>
        `;
    }
}


/* =========================================
   AMENITY HTML
========================================= */

function amenityHTML(
    icon,
    name,
    distance
) {

    return `

        <div class="amenity">

            ${icon} ${name}

            <span>
                ${distance} km
            </span>

        </div>

    `;
}