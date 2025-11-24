# Food Waste Tracking & Donation Database

**SDG Innovators - Group 10**

## Team Members
- **Rupinder Kaur** (249475730) - Project Lead
- **Hirak Rakeshkumar Patel** (259692150)
- **Yamini Rahul Patel** (249404750)

## Project Overview

The Food Waste Tracking & Donation Database is a web-based application designed to address **UN Sustainable Development Goal 2: Zero Hunger**. This project aims to create a centralized platform that connects food donors (restaurants, households, grocery stores) with NGOs and organizations serving vulnerable populations.

### Problem Statement
- Approximately 1.3 billion tons of food is wasted globally each year
- Millions of people suffer from chronic hunger and malnutrition
- Lack of efficient systems to connect food donors with organizations serving those in need
- Environmental impact from food waste (greenhouse gas emissions, wasted resources)

### Solution
A database-driven web application that enables:
- **Food Donors** to log surplus food items with details (type, quantity, expiry date)
- **NGOs** to browse, search, and claim available food donations
- Real-time tracking of donation status and pickup coordination
- Reduction of food waste while addressing hunger in local communities

## Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Database management
- **SQLAlchemy** - Object-Relational Mapping (ORM)
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and validation

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - Responsive framework
- **JavaScript** - Interactive features
- **Jinja2** - Template engine

## Key Features

### For Food Donors
- ✅ User registration and authentication
- ✅ Add, edit, and delete food donation records
- ✅ View donation history and status updates
- ✅ Receive notifications when donations are claimed

### For NGOs
- ✅ Browse available food donations
- ✅ Advanced search and filtering (location, food type, expiry date)
- ✅ Claim food donations for pickup
- ✅ Track claimed donations and pickup history

### System Features
- ✅ Role-based access control (Donor vs NGO)
- ✅ Real-time status updates
- ✅ Data validation and security measures
- ✅ Responsive design for mobile and desktop
- ✅ CRUD operations for all entities

## Project Structure
```
food-waste-tracker/
├── app/
│   ├── __init__.py
│   ├── models/          # Database models
│   ├── routes/          # Application routes/controllers
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   └── forms/           # WTForms definitions
├── migrations/          # Database migrations
├── tests/              # Unit and integration tests
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── run.py             # Application entry point
└── README.md          # Project documentation
```

## Development Phases

### Phase 1: Foundation & Planning ✅
- [x] Requirements analysis
- [x] Database design and ERD
- [x] System architecture planning

### Phase 2: Backend Development
- [ ] Database schema implementation
- [ ] User authentication system
- [ ] Core API development (CRUD operations)
- [ ] Food donation management logic

### Phase 3: Frontend Development
- [ ] UI/UX design and wireframes
- [ ] Template implementation
- [ ] Frontend-backend integration
- [ ] Responsive design with Bootstrap

### Phase 4: Features & Enhancement
- [ ] Advanced search and filtering
- [ ] Notification system
- [ ] Reporting dashboard
- [ ] User experience improvements

### Phase 5: Testing & Deployment
- [ ] Unit and integration testing
- [ ] Documentation completion
- [ ] Local deployment setup
- [ ] User acceptance testing

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd food-waste-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate
flask db upgrade

# Run the application
python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Impact & Goals

### Environmental Impact
- Reduce food waste in landfills
- Lower carbon emissions from food waste
- Promote sustainable food systems

### Social Impact
- Address hunger and food insecurity
- Connect surplus food with those in need
- Build stronger community networks
- Support NGOs and charitable organizations

### Technical Learning
- Database design and management
- Web application development
- User authentication and security
- RESTful API design
- Responsive web design

## References

1. Campi, M., Dueñas, M., & Fagiolo, G. (2021). "Specialization in food production affects global food security and food systems sustainability." *World Development*, 141, 105411.

2. Filimonau, V., Zhang, H., & Wang, L. (2020). "Food waste management in Shanghai full-service restaurants: A senior managers' perspective." *Journal of Cleaner Production*, 258, 120975.

3. Roy, P., Mohanty, A. K., Dick, P., & Misra, M. (2023). "A Review on the Challenges and Choices for Food Waste Valorization: Environmental and Economic Impacts." *ACS Environmental Au*, 3(2), 58–75.

## License

This project is developed for educational purposes as part of the Database course at Algoma University.

---

**Project Timeline:** Fall 2025  
**Course:** Database Systems  
**Institution:** Algoma University  
**Last Updated:** September 29, 2025