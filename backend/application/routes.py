from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.models import User, ParkingLot, ParkingSpot, Reservation
from application.database import db
from application.security import generate_tokens, admin_required, user_required, revoke_token
# from application.cache_services import CachedDashboardService, CachedParkingService, invalidate_related_caches, get_cache_status
# Celery tasks will be imported conditionally when needed
from datetime import datetime
import os

def create_routes(app):
    """Create all API routes"""
    
    # ==================== TEST ROUTE ====================
    @app.route('/api/test', methods=['GET'])
    def test():
        """Simple test endpoint"""
        return jsonify({'message': 'Backend is working!', 'status': 'success'}), 200
    
    # ==================== CORS PREFLIGHT ====================
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        """Handle CORS preflight requests"""
        return '', 200
    
    # ==================== AUTH ROUTES ====================
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """User/Admin login with enhanced role-based response"""
        try:
            data = request.get_json()
            print(f"Login attempt - received data: {data}")  # Debug log
            
            username = data.get('username')
            password = data.get('password')
            
            print(f"Username: {username}, Password length: {len(password) if password else 0}")  # Debug log
            
            if not username or not password:
                return jsonify({'message': 'Username and password required'}), 400
            
            user = User.query.filter_by(username=username).first()
            print(f"User found: {user}")  # Debug log
            
            if user and user.verify_password(password) and user.is_active:
                print(f"Password verification successful for user: {user.username}, role: {user.role}")  # Debug log
                tokens = generate_tokens(user)
                
                # Enhanced response with clear role information
                response_data = {
                    'message': f'Login successful - Welcome {user.role}!',
                    'data': {
                        'access_token': tokens['access_token'],
                        'refresh_token': tokens['refresh_token'],
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'role': user.role,
                            'is_admin': user.is_admin(),
                            'created_at': user.created_at.isoformat(),
                            'is_active': user.is_active
                        }
                    }
                }
                
                return jsonify(response_data), 200
            else:
                print(f"Login failed - User: {user}, Password valid: {user.verify_password(password) if user else False}, Active: {user.is_active if user else False}")  # Debug log
                return jsonify({'message': 'Invalid username or password'}), 401
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # Debug log
            return jsonify({'message': 'Login failed. Please try again.'}), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """User registration (only for regular users)"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not all([username, email, password]):
                return jsonify({'message': 'All fields are required'}), 400
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                return jsonify({'message': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'message': 'Email already exists'}), 400
            
            # Create new user with default 'user' role
            new_user = User(
                username=username,
                email=email,
                password=password,
                role='user'
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            tokens = generate_tokens(new_user)
            return jsonify({
                'message': 'Registration successful',
                'data': tokens
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Logout user"""
        try:
            revoke_token()
            return jsonify({'message': 'Logout successful'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    @user_required
    def get_profile():
        """Get user profile"""
        try:
            user_id = int(get_jwt_identity())  # Convert to int
            user = User.query.get(user_id)
            return jsonify({
                'message': 'Profile retrieved successfully',
                'data': user.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @app.route('/api/auth/profile', methods=['PUT'])
    @user_required
    def update_profile():
        """Update user profile"""
        try:
            user_id = int(get_jwt_identity())  # Convert to int
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            data = request.get_json()
            
            # Update allowed fields
            if 'email' in data:
                # Check if email is already taken by another user
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({'message': 'Email already exists'}), 400
                user.email = data['email']
            
            if 'name' in data:
                user.name = data['name']
            
            # Save changes
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'data': user.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/auth/whoami', methods=['GET'])
    @jwt_required()
    def whoami():
        """Get current authenticated user info - useful for frontend"""
        try:
            user_id = int(get_jwt_identity())  # Convert to int
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            return jsonify({
                'message': 'Current user retrieved successfully',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_admin': user.is_admin(),
                    'is_active': user.is_active
                }
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== PARKING LOT ROUTES ====================
    
    @app.route('/api/parking-lots', methods=['GET'])
    @user_required
    def get_parking_lots():
        """Get all parking lots with cached availability information"""
        try:
            # Check if force refresh is requested
            force_refresh = request.args.get('refresh', 'false').lower() == 'true'
            
            # Get cached parking lots with availability
            lots_data = CachedParkingService.get_parking_lots_with_availability(force_refresh)
            
            return jsonify({
                'message': 'Parking lots retrieved successfully',
                'data': lots_data,
                'cache_info': {
                    'refresh_hint': 'Add ?refresh=true to force refresh',
                    'data_includes': 'Real-time availability and occupancy rates'
                }
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/parking-lots/<int:lot_id>', methods=['GET'])
    @user_required
    def get_parking_lot(lot_id):
        """Get specific parking lot with cached detailed information"""
        try:
            # Check if force refresh is requested
            force_refresh = request.args.get('refresh', 'false').lower() == 'true'
            
            # Get cached parking lot details
            lot_data = CachedParkingService.get_parking_lot_details(lot_id, force_refresh)
            
            if not lot_data:
                return jsonify({'message': 'Parking lot not found'}), 404
            
            return jsonify({
                'message': 'Parking lot retrieved successfully',
                'data': lot_data,
                'cache_info': {
                    'generated_at': lot_data.get('_generated_at'),
                    'refresh_hint': 'Add ?refresh=true to force refresh'
                }
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/parking-lots', methods=['POST'])
    @admin_required
    def create_parking_lot():
        """Create new parking lot (Admin only)"""
        try:
            data = request.get_json()
            
            required_fields = ['prime_location_name', 'address', 'pin_code', 'price_per_hour', 'number_of_spots']
            if not all(field in data for field in required_fields):
                return jsonify({'message': 'All fields are required'}), 400
            
            # Create parking lot
            new_lot = ParkingLot(
                prime_location_name=data['prime_location_name'],
                address=data['address'],
                pin_code=data['pin_code'],
                price_per_hour=float(data['price_per_hour']),
                number_of_spots=int(data['number_of_spots'])
            )
            
            db.session.add(new_lot)
            db.session.flush()  # Get the lot ID
            
            # Create parking spots
            for i in range(1, new_lot.number_of_spots + 1):
                spot = ParkingSpot(
                    spot_number=f"A{i}",  # Simple numbering: A1, A2, A3...
                    lot_id=new_lot.id
                )
                db.session.add(spot)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Parking lot created successfully',
                'data': new_lot.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/parking-lots/<int:lot_id>', methods=['PUT'])
    @admin_required
    def update_parking_lot(lot_id):
        """Update parking lot (Admin only)"""
        try:
            lot = ParkingLot.query.get_or_404(lot_id)
            data = request.get_json()
            
            # Update basic info
            if 'prime_location_name' in data:
                lot.prime_location_name = data['prime_location_name']
            if 'address' in data:
                lot.address = data['address']
            if 'pin_code' in data:
                lot.pin_code = data['pin_code']
            if 'price_per_hour' in data:
                lot.price_per_hour = float(data['price_per_hour'])
            
            # Handle spots number change
            if 'number_of_spots' in data:
                new_spot_count = int(data['number_of_spots'])
                current_spot_count = lot.number_of_spots
                
                if new_spot_count > current_spot_count:
                    # Add new spots
                    for i in range(current_spot_count + 1, new_spot_count + 1):
                        spot = ParkingSpot(
                            spot_number=f"A{i}",
                            lot_id=lot.id
                        )
                        db.session.add(spot)
                elif new_spot_count < current_spot_count:
                    # Remove spots (only if they're available)
                    spots_to_remove = ParkingSpot.query.filter(
                        ParkingSpot.lot_id == lot_id,
                        ParkingSpot.status == 'A'
                    ).order_by(ParkingSpot.id.desc()).limit(current_spot_count - new_spot_count).all()
                    
                    if len(spots_to_remove) < (current_spot_count - new_spot_count):
                        return jsonify({'message': 'Cannot remove occupied spots'}), 400
                    
                    for spot in spots_to_remove:
                        db.session.delete(spot)
                
                lot.number_of_spots = new_spot_count
            
            lot.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Parking lot updated successfully',
                'data': lot.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/parking-lots/<int:lot_id>', methods=['DELETE'])
    @admin_required
    def delete_parking_lot(lot_id):
        """Delete parking lot (Admin only)"""
        try:
            lot = ParkingLot.query.get_or_404(lot_id)
            
            # Check if any spots are occupied
            occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
            if occupied_spots > 0:
                return jsonify({'message': 'Cannot delete lot with occupied spots'}), 400
            
            # Delete the lot (spots will be deleted by cascade)
            db.session.delete(lot)
            db.session.commit()
            
            return jsonify({'message': 'Parking lot deleted successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    # ==================== RESERVATION ROUTES ====================
    
    @app.route('/api/reservations', methods=['POST'])
    @user_required
    def create_reservation():
        """Book a parking spot"""
        try:
            data = request.get_json()
            lot_id = data.get('lot_id')
            vehicle_number = data.get('vehicle_number')
            remarks = data.get('remarks')  # Optional remarks field
            
            if not lot_id:
                return jsonify({'message': 'Parking lot ID is required'}), 400
            
            user_id = int(get_jwt_identity())  # Convert to int
            
            # Check if user already has an active reservation
            # active_reservation = Reservation.query.filter_by(
            #     user_id=user_id,
            #     leaving_timestamp=None
            # ).first()
            
            # if active_reservation:
            #     return jsonify({'message': 'You already have an active reservation'}), 400
            
            # Find first available spot in the lot
            available_spot = ParkingSpot.query.filter_by(
                lot_id=lot_id,
                status='A'
            ).first()
            
            if not available_spot:
                return jsonify({'message': 'No available spots in this lot'}), 400
            
            # Create reservation
            reservation = Reservation(
                spot_id=available_spot.id,
                user_id=user_id,
                vehicle_number=vehicle_number,
                remarks=remarks
            )
            
            # Update spot status
            available_spot.status = 'O'
            
            db.session.add(reservation)
            db.session.commit()
            
            # Invalidate related caches since parking availability changed
            invalidate_related_caches('reservation', user_id=user_id, lot_id=lot_id)
            
            return jsonify({
                'message': 'Parking spot booked successfully',
                'data': reservation.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/reservations/<int:reservation_id>/release', methods=['PUT'])
    @user_required
    def release_parking_spot(reservation_id):
        """Release/vacate parking spot"""
        try:
            user_id = int(get_jwt_identity())  # Convert to int
            reservation = Reservation.query.filter_by(
                id=reservation_id,
                user_id=user_id,
                leaving_timestamp=None
            ).first()
            
            if not reservation:
                return jsonify({'message': 'Active reservation not found'}), 404
            
            # Update reservation
            reservation.leaving_timestamp = datetime.utcnow()
            reservation.calculate_cost()
            
            # Update spot status
            reservation.parking_spot.status = 'A'
            
            db.session.commit()
            
            # Invalidate related caches since parking availability changed
            invalidate_related_caches('reservation', user_id=user_id)
            
            return jsonify({
                'message': 'Parking spot released successfully',
                'data': reservation.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/reservations', methods=['GET'])
    @user_required
    def get_user_reservations():
        """Get user's reservations"""
        try:
            user_id = int(get_jwt_identity())  # Convert to int
            reservations = Reservation.query.filter_by(user_id=user_id).order_by(
                Reservation.created_at.desc()
            ).all()
            
            # Add parking lot and spot information to each reservation
            reservation_data = []
            for reservation in reservations:
                data = reservation.to_dict()
                
                # Get parking spot and lot information
                spot = ParkingSpot.query.get(reservation.spot_id)
                if spot:
                    lot = ParkingLot.query.get(spot.lot_id)
                    if lot:
                        data['parking_lot_name'] = lot.prime_location_name
                        data['parking_lot_address'] = lot.address
                        data['spot_number'] = spot.spot_number
                        data['price_per_hour'] = lot.price_per_hour
                
                reservation_data.append(data)
            
            return jsonify({
                'message': 'Reservations retrieved successfully',
                'data': reservation_data
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== ADMIN DASHBOARD ROUTES ====================
    
    @app.route('/api/admin/dashboard', methods=['GET'])
    @admin_required
    def admin_dashboard():
        """Get cached admin dashboard data with performance boost"""
        try:
            # Check if force refresh is requested
            force_refresh = request.args.get('refresh', 'false').lower() == 'true'
            
            # Get cached dashboard statistics
            dashboard_data = CachedDashboardService.get_admin_dashboard_stats(force_refresh)
            
            return jsonify({
                'message': 'Dashboard data retrieved successfully',
                'data': dashboard_data,
                'cache_info': {
                    'cached': dashboard_data.get('_cached', False),
                    'generated_at': dashboard_data.get('_generated_at'),
                    'refresh_hint': 'Add ?refresh=true to force refresh'
                }
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_all_users():
        """Get all registered users"""
        try:
            users = User.query.filter_by(role='user').all()
            return jsonify({
                'message': 'Users retrieved successfully',
                'data': [user.to_dict() for user in users]
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/reservations', methods=['GET'])
    @admin_required
    def get_all_reservations():
        """Get all reservations"""
        try:
            reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
            
            # Add parking lot and spot information to each reservation
            reservation_data = []
            for reservation in reservations:
                data = reservation.to_dict()
                
                # Get user information
                user = User.query.get(reservation.user_id)
                if user:
                    data['user_name'] = user.username
                
                # Get parking spot and lot information
                spot = ParkingSpot.query.get(reservation.spot_id)
                if spot:
                    lot = ParkingLot.query.get(spot.lot_id)
                    if lot:
                        data['parking_lot_name'] = lot.prime_location_name
                        data['parking_lot_address'] = lot.address
                        data['spot_number'] = spot.spot_number
                        data['price_per_hour'] = lot.price_per_hour
                
                reservation_data.append(data)
            
            return jsonify({
                'message': 'Reservations retrieved successfully',
                'data': reservation_data
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== CSV EXPORT ROUTES ====================
    
    @app.route('/api/export/csv', methods=['POST'])
    @user_required
    def trigger_csv_export():
        """Trigger CSV export for user data"""
        try:
            user_id = get_jwt_identity()
            
            # Try to use Celery if available
            try:
                from application.tasks import export_user_data_csv
                task = export_user_data_csv.delay(user_id)
                
                return jsonify({
                    'message': 'CSV export initiated successfully',
                    'task_id': task.id,
                    'status': 'processing'
                }), 200
                
            except (ImportError, Exception) as e:
                # Fallback to synchronous export if Celery is not available
                from application.tasks import export_user_data_csv_sync
                result = export_user_data_csv_sync(user_id)
                
                return jsonify({
                    'message': 'CSV export completed (synchronous)',
                    'result': result,
                    'status': 'completed'
                }), 200
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/export/download/<filename>', methods=['GET'])
    @user_required
    def download_csv(filename):
        """Download CSV file"""
        try:
            filepath = os.path.join('static', 'exports', filename)
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)
            else:
                return jsonify({'message': 'File not found'}), 404
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== SEARCH ENDPOINTS ====================
    
    @app.route('/api/admin/search', methods=['GET'])
    @admin_required
    def admin_search():
        """Admin search functionality - search users, parking lots, and spots"""
        try:
            search_type = request.args.get('type')
            search_query = request.args.get('query', '').strip()
            
            if not search_type or not search_query:
                return jsonify({'message': 'Search type and query required'}), 400
            
            results = []
            
            if search_type == 'user_id':
                try:
                    user_id = int(search_query)
                    user = User.query.filter_by(id=user_id).first()
                    if user:
                        reservation_count = Reservation.query.filter_by(user_id=user.id).count()
                        results.append({
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'role': user.role,
                            'is_active': user.is_active,
                            'total_reservations': reservation_count
                        })
                except ValueError:
                    pass
                    
            elif search_type == 'username':
                users = User.query.filter(
                    db.func.lower(User.username).like(f'%{search_query.lower()}%')
                ).all()
                for user in users:
                    reservation_count = Reservation.query.filter_by(user_id=user.id).count()
                    results.append({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_active': user.is_active,
                        'total_reservations': reservation_count
                    })
                    
            elif search_type == 'lot_location':
                lots = ParkingLot.query.filter(
                    db.or_(
                        db.func.lower(ParkingLot.prime_location_name).like(f'%{search_query.lower()}%'),
                        db.func.lower(ParkingLot.address).like(f'%{search_query.lower()}%'),
                        ParkingLot.pin_code.like(f'%{search_query}%')
                    )
                ).all()
                for lot in lots:
                    available_spots = ParkingSpot.query.filter_by(
                        lot_id=lot.id, 
                        status='A'
                    ).count()
                    results.append({
                        'id': lot.id,
                        'prime_location_name': lot.prime_location_name,
                        'address': lot.address,
                        'pin_code': lot.pin_code,
                        'price_per_hour': lot.price_per_hour,
                        'number_of_spots': lot.number_of_spots,
                        'available_spots_count': available_spots
                    })
                    
            elif search_type == 'spot_location':
                # Search spots by parking lot location - more flexible matching
                lots = ParkingLot.query.filter(
                    db.or_(
                        db.func.lower(ParkingLot.prime_location_name).like(f'%{search_query.lower()}%'),
                        db.func.lower(ParkingLot.address).like(f'%{search_query.lower()}%'),
                        ParkingLot.pin_code.like(f'%{search_query}%')
                    )
                ).all()
                
                for lot in lots:
                    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
                    for spot in spots:
                        current_user = None
                        reserved_since = None
                        if spot.status == 'O':  # 'O' means Occupied
                            reservation = Reservation.query.filter_by(
                                spot_id=spot.id,
                                status='active'
                            ).first()
                            if reservation:
                                current_user = reservation.user.username
                                reserved_since = reservation.start_time.isoformat()
                        
                        results.append({
                            'id': spot.id,
                            'lot_name': lot.prime_location_name,
                            'location': lot.address,
                            'is_available': spot.status == 'A',
                            'current_user': current_user,
                            'reserved_since': reserved_since
                        })
            
            return jsonify({
                'status': 'success',
                'data': results,
                'count': len(results)
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/search', methods=['GET'])
    @user_required
    def user_search():
        """User search functionality - search parking lots and spots"""
        try:
            search_query = request.args.get('query', '').strip()
            search_type = request.args.get('type', 'lots').strip().lower()  # 'lots' or 'spots'
            
            if not search_query:
                return jsonify({'message': 'Search query required'}), 400
            
            if search_type not in ['lots', 'spots']:
                return jsonify({'message': 'Search type must be "lots" or "spots"'}), 400
            
            # Make search query more flexible - convert to lowercase for case-insensitive search
            search_pattern = f'%{search_query.lower()}%'
            
            if search_type == 'lots':
                # Search parking lots with more flexible matching
                lots = ParkingLot.query.filter(
                    db.or_(
                        db.func.lower(ParkingLot.prime_location_name).like(search_pattern),
                        db.func.lower(ParkingLot.address).like(search_pattern),
                        ParkingLot.pin_code.like(search_pattern)
                    )
                ).all()
                
                results = []
                for lot in lots:
                    available_spots = ParkingSpot.query.filter_by(
                        lot_id=lot.id, 
                        status='A'
                    ).count()
                    results.append({
                        'id': lot.id,
                        'type': 'lot',
                        'prime_location_name': lot.prime_location_name,
                        'address': lot.address,
                        'pin_code': lot.pin_code,
                        'price_per_hour': lot.price_per_hour,
                        'number_of_spots': lot.number_of_spots,
                        'available_spots_count': available_spots
                    })
            
            else:  # search_type == 'spots'
                # Search parking spots with their lot information - more flexible matching
                spots = db.session.query(ParkingSpot, ParkingLot).join(
                    ParkingLot, ParkingSpot.lot_id == ParkingLot.id
                ).filter(
                    db.or_(
                        db.func.lower(ParkingSpot.spot_number).like(search_pattern),
                        db.func.lower(ParkingLot.prime_location_name).like(search_pattern),
                        db.func.lower(ParkingLot.address).like(search_pattern),
                        ParkingLot.pin_code.like(search_pattern)
                    )
                ).all()
                
                results = []
                for spot, lot in spots:
                    results.append({
                        'id': spot.id,
                        'type': 'spot',
                        'spot_number': spot.spot_number,
                        'is_available': spot.status == 'A',
                        'lot_id': spot.lot_id,
                        'prime_location_name': lot.prime_location_name,
                        'address': lot.address,
                        'pin_code': lot.pin_code,
                        'price_per_hour': lot.price_per_hour,
                        'created_at': spot.created_at.isoformat() if spot.created_at else None
                    })
            
            return jsonify({
                'status': 'success',
                'data': results,
                'count': len(results)
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== SUMMARY ENDPOINTS ====================
    
    @app.route('/api/admin/summary', methods=['GET'])
    @admin_required
    def admin_summary():
        """Admin summary dashboard with analytics"""
        try:
            # Get total revenue
            total_revenue = db.session.query(
                db.func.sum(Reservation.parking_cost)
            ).filter(
                Reservation.leaving_timestamp.isnot(None)
            ).scalar() or 0
            
            # Get average occupancy
            total_spots = ParkingSpot.query.count()
            occupied_spots = ParkingSpot.query.filter_by(status='O').count()
            avg_occupancy = round((occupied_spots / total_spots * 100), 2) if total_spots > 0 else 0
            
            # Get active users count
            active_users = User.query.filter_by(is_active=True, role='user').count()
            
            # Get average parking duration
            avg_duration_query = db.session.query(
                db.func.avg(
                    db.func.extract('epoch', Reservation.leaving_timestamp - Reservation.parking_timestamp) / 3600
                )
            ).filter(
                Reservation.leaving_timestamp.isnot(None)
            ).scalar()
            avg_duration = round(avg_duration_query, 2) if avg_duration_query else 0
            
            # Revenue by parking lot
            revenue_by_lot = {}
            revenue_results = db.session.query(
                ParkingLot.prime_location_name,
                db.func.sum(Reservation.parking_cost).label('total_revenue')
            ).join(
                ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
            ).join(
                Reservation, ParkingSpot.id == Reservation.spot_id
            ).filter(
                Reservation.leaving_timestamp.isnot(None)
            ).group_by(ParkingLot.id).all()
            
            for lot_name, revenue in revenue_results:
                revenue_by_lot[lot_name] = float(revenue) if revenue else 0
            
            # Occupancy by parking lot
            occupancy_by_lot = []
            lots = ParkingLot.query.all()
            for lot in lots:
                occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
                available = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
                total = occupied + available
                occupancy_percentage = round((occupied / total * 100), 2) if total > 0 else 0
                
                occupancy_by_lot.append({
                    'name': lot.prime_location_name,
                    'occupied': occupied,
                    'available': available,
                    'occupancy_percentage': occupancy_percentage
                })
            
            # Monthly revenue trend (last 6 months)
            monthly_revenue = []
            from datetime import datetime, timedelta
            import calendar
            
            current_date = datetime.now()
            for i in range(6):
                # Calculate start of month
                if i == 0:
                    month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                else:
                    # Go back i months
                    year = current_date.year
                    month = current_date.month - i
                    while month <= 0:
                        month += 12
                        year -= 1
                    month_start = datetime(year, month, 1)
                
                # Calculate end of month
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1)
                
                month_revenue = db.session.query(
                    db.func.sum(Reservation.parking_cost)
                ).filter(
                    Reservation.leaving_timestamp >= month_start,
                    Reservation.leaving_timestamp < month_end,
                    Reservation.leaving_timestamp.isnot(None)
                ).scalar() or 0
                
                month_reservations = Reservation.query.filter(
                    Reservation.parking_timestamp >= month_start,
                    Reservation.parking_timestamp < month_end
                ).count()
                
                monthly_revenue.append({
                    'month': month_start.strftime('%B %Y'),
                    'revenue': float(month_revenue),
                    'reservations': month_reservations
                })
            
            # Reverse to show oldest to newest
            monthly_revenue.reverse()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'total_revenue': float(total_revenue),
                    'avg_occupancy': avg_occupancy,
                    'active_users': active_users,
                    'avg_duration': avg_duration,
                    'revenue_by_lot': revenue_by_lot,
                    'occupancy_by_lot': occupancy_by_lot,
                    'monthly_revenue': monthly_revenue
                }
            }), 200
            
        except Exception as e:
            print(f"Admin summary error: {str(e)}")  # Debug log
            return jsonify({'message': str(e)}), 500

    @app.route('/api/user/summary', methods=['GET'])
    @user_required
    def user_summary():
        """User summary dashboard with personal stats"""
        try:
            user_id = int(get_jwt_identity())
            
            # Get user's total reservations
            total_reservations = Reservation.query.filter_by(user_id=user_id).count()
            
            # Get user's active reservations
            active_reservations = Reservation.query.filter_by(
                user_id=user_id,
                leaving_timestamp=None
            ).count()
            
            # Get user's completed reservations
            completed_reservations = Reservation.query.filter(
                Reservation.user_id == user_id,
                Reservation.leaving_timestamp.isnot(None)
            ).count()
            
            # Get user's total spending
            total_spending = db.session.query(
                db.func.sum(Reservation.parking_cost)
            ).filter(
                Reservation.user_id == user_id,
                Reservation.leaving_timestamp.isnot(None)
            ).scalar() or 0
            
            # Get user's total hours parked
            total_hours = db.session.query(
                db.func.sum(
                    db.func.extract('epoch', Reservation.leaving_timestamp - Reservation.parking_timestamp) / 3600
                )
            ).filter(
                Reservation.user_id == user_id,
                Reservation.leaving_timestamp.isnot(None)
            ).scalar() or 0
            
            # Get user's favorite parking lot (most used)
            favorite_lot_result = db.session.query(
                ParkingLot.prime_location_name,
                db.func.count(Reservation.id).label('usage_count')
            ).join(
                ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
            ).join(
                Reservation, ParkingSpot.id == Reservation.spot_id
            ).filter(
                Reservation.user_id == user_id
            ).group_by(ParkingLot.id).order_by(
                db.func.count(Reservation.id).desc()
            ).first()
            
            favorite_lot = favorite_lot_result[0] if favorite_lot_result else 'N/A'
            
            # Get monthly usage (last 6 months)
            monthly_usage = []
            from datetime import datetime, timedelta
            import calendar
            
            current_date = datetime.now()
            for i in range(6):
                # Calculate start of month
                if i == 0:
                    month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                else:
                    # Go back i months
                    year = current_date.year
                    month = current_date.month - i
                    while month <= 0:
                        month += 12
                        year -= 1
                    month_start = datetime(year, month, 1)
                
                # Calculate end of month
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1)
                
                month_spending = db.session.query(
                    db.func.sum(Reservation.parking_cost)
                ).filter(
                    Reservation.user_id == user_id,
                    Reservation.leaving_timestamp >= month_start,
                    Reservation.leaving_timestamp < month_end,
                    Reservation.leaving_timestamp.isnot(None)
                ).scalar() or 0
                
                month_hours = db.session.query(
                    db.func.sum(
                        db.func.extract('epoch', Reservation.leaving_timestamp - Reservation.parking_timestamp) / 3600
                    )
                ).filter(
                    Reservation.user_id == user_id,
                    Reservation.leaving_timestamp >= month_start,
                    Reservation.leaving_timestamp < month_end,
                    Reservation.leaving_timestamp.isnot(None)
                ).scalar() or 0
                
                monthly_usage.append({
                    'month': month_start.strftime('%B %Y'),
                    'hours': round(float(month_hours), 2),
                    'spent': float(month_spending)
                })
            
            # Reverse to show oldest to newest
            monthly_usage.reverse()
            
            # Get locations used by user
            locations_used = []
            location_results = db.session.query(
                ParkingLot.prime_location_name,
                db.func.count(Reservation.id).label('usage_count'),
                db.func.sum(
                    db.func.extract('epoch', Reservation.leaving_timestamp - Reservation.parking_timestamp) / 3600
                ).label('total_hours')
            ).join(
                ParkingSpot, ParkingLot.id == ParkingSpot.lot_id
            ).join(
                Reservation, ParkingSpot.id == Reservation.spot_id
            ).filter(
                Reservation.user_id == user_id,
                Reservation.leaving_timestamp.isnot(None)
            ).group_by(ParkingLot.id).all()
            
            for name, count, hours in location_results:
                locations_used.append({
                    'name': name,
                    'count': count,
                    'hours': round(float(hours), 2) if hours else 0
                })
            
            # Get user's recent reservations (last 5)
            recent_reservations_query = db.session.query(Reservation).filter(
                Reservation.user_id == user_id
            ).order_by(Reservation.parking_timestamp.desc()).limit(5).all()
            
            recent_reservations = []
            for reservation in recent_reservations_query:
                spot = ParkingSpot.query.get(reservation.spot_id)
                lot = ParkingLot.query.get(spot.lot_id) if spot else None
                
                recent_reservations.append({
                    'id': reservation.id,
                    'location': lot.prime_location_name if lot else 'Unknown',
                    'parking_timestamp': reservation.parking_timestamp.isoformat(),
                    'leaving_timestamp': reservation.leaving_timestamp.isoformat() if reservation.leaving_timestamp else None,
                    'duration_hours': round(reservation.get_duration(), 2),
                    'parking_cost': float(reservation.parking_cost),
                    'is_active': reservation.is_active()
                })
            
            return jsonify({
                'status': 'success',
                'data': {
                    'total_reservations': total_reservations,
                    'active_reservations': active_reservations,
                    'completed_reservations': completed_reservations,
                    'total_spending': float(total_spending),
                    'total_hours': round(float(total_hours), 2),
                    'favorite_lot': favorite_lot,
                    'monthly_usage': monthly_usage,
                    'locations_used': locations_used,
                    'recent_reservations': recent_reservations
                }
            }), 200
            
        except Exception as e:
            print(f"User summary error: {str(e)}")  # Debug log
            return jsonify({'message': str(e)}), 500
    
    # ==================== BACKGROUND TASKS AND CSV EXPORT ====================
    
    @app.route('/api/export/csv', methods=['POST'])
    @user_required
    def request_csv_export():
        """Request CSV export of user's parking history"""
        try:
            user_id = int(get_jwt_identity())
            
            # Try to use Celery if available
            try:
                from application.tasks import export_user_data_csv
                task = export_user_data_csv.delay(user_id)
                
                return jsonify({
                    'message': 'CSV export request submitted',
                    'task_id': task.id,
                    'status': 'processing'
                }), 202
                
            except Exception as celery_error:
                # Fallback to synchronous export if Celery is not available
                print(f"Celery not available, using synchronous export: {str(celery_error)}")
                
                # Import and run synchronous version
                from application.tasks import export_user_data_csv_sync
                result = export_user_data_csv_sync(user_id)
                
                return jsonify({
                    'message': 'CSV export completed (synchronous)',
                    'result': result,
                    'status': 'completed'
                }), 200
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/tasks/trigger-reminders', methods=['POST'])
    @admin_required
    def trigger_daily_reminders():
        """Manually trigger daily reminders (Admin only)"""
        try:
            # Try to use Celery if available
            try:
                from application.tasks import send_daily_reminders
                task = send_daily_reminders.delay()
                
                return jsonify({
                    'message': 'Daily reminders task submitted',
                    'task_id': task.id,
                    'status': 'processing'
                }), 202
                
            except Exception as celery_error:
                # Fallback to synchronous version
                print(f"Celery not available, using synchronous version: {str(celery_error)}")
                
                from application.tasks import send_daily_reminders_sync
                result = send_daily_reminders_sync()
                
                return jsonify({
                    'message': 'Daily reminders completed (synchronous)',
                    'result': result,
                    'status': 'completed'
                }), 200
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/tasks/trigger-reports', methods=['POST'])
    @admin_required
    def trigger_monthly_reports():
        """Manually trigger monthly reports (Admin only)"""
        try:
            # Try to use Celery if available
            try:
                from application.tasks import send_monthly_reports
                task = send_monthly_reports.delay()
                
                return jsonify({
                    'message': 'Monthly reports task submitted',
                    'task_id': task.id,
                    'status': 'processing'
                }), 202
                
            except Exception as celery_error:
                # Fallback to synchronous version
                print(f"Celery not available, using synchronous version: {str(celery_error)}")
                
                from application.tasks import send_monthly_reports_sync
                result = send_monthly_reports_sync()
                
                return jsonify({
                    'message': 'Monthly reports completed (synchronous)',
                    'result': result,
                    'status': 'completed'
                }), 200
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/tasks/status/<task_id>', methods=['GET'])
    @admin_required
    def get_task_status(task_id):
        """Get status of a background task (Admin only)"""
        try:
            # Try to check Celery task status
            try:
                celery_app = app.extensions.get('celery')
                if celery_app:
                    task_result = celery_app.AsyncResult(task_id)
                    
                    return jsonify({
                        'task_id': task_id,
                        'status': task_result.status,
                        'result': task_result.result if task_result.ready() else None,
                        'info': task_result.info
                    }), 200
                else:
                    return jsonify({
                        'message': 'Celery not available',
                        'task_id': task_id,
                        'status': 'unavailable'
                    }), 503
                    
            except Exception as celery_error:
                return jsonify({
                    'message': f'Error checking task status: {str(celery_error)}',
                    'task_id': task_id,
                    'status': 'error'
                }), 500
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # ==================== CACHE MANAGEMENT ====================
    
    @app.route('/api/admin/cache/status', methods=['GET'])
    @admin_required
    def get_cache_status_route():
        """Get current cache status and performance metrics (Admin only)"""
        try:
            cache_stats = get_cache_status()
            
            return jsonify({
                'message': 'Cache status retrieved successfully',
                'data': cache_stats
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/cache/clear', methods=['POST'])
    @admin_required
    def clear_cache():
        """Clear all cached data (Admin only)"""
        try:
            from application.cache import app_cache
            
            # Get stats before clearing
            stats_before = app_cache.get_stats()
            
            # Clear all cache
            app_cache.clear()
            
            return jsonify({
                'message': 'Cache cleared successfully',
                'cleared_items': stats_before['total_items'],
                'status': 'success'
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @app.route('/api/admin/cache/cleanup', methods=['POST'])
    @admin_required
    def cleanup_expired_cache():
        """Clean up expired cache entries (Admin only)"""
        try:
            from application.cache import app_cache
            
            # Clean up expired entries
            expired_count = app_cache.cleanup_expired()
            
            return jsonify({
                'message': 'Expired cache entries cleaned up',
                'removed_items': expired_count,
                'status': 'success'
            }), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    # ==================== EMAIL TESTING ROUTES ====================
    
    @app.route('/api/test/email', methods=['POST'])
    @admin_required
    def test_email():
        """Test email functionality (Admin only)"""
        try:
            data = request.get_json()
            recipient = data.get('recipient')
            
            if not recipient:
                return jsonify({'message': 'Recipient email is required'}), 400
            
            # Try to send test email using Celery
            try:
                from application.tasks import send_test_email
                task = send_test_email.delay(recipient)
                
                return jsonify({
                    'message': 'Test email task submitted to Celery queue',
                    'task_id': task.id,
                    'recipient': recipient,
                    'status': 'queued'
                }), 202
                
            except Exception as celery_error:
                # Fallback to immediate email sending
                from application.mail import send_email
                
                success = send_email(
                    to=recipient,
                    subject="Test Email from Parking App",
                    template="""
                    <html>
                    <body>
                        <h2>Test Email</h2>
                        <p>This is a test email from your Vehicle Parking System!</p>
                        <p>If you received this, your email configuration is working correctly.</p>
                        <p>Sent at: {}</p>
                    </body>
                    </html>
                    """.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
                )
                
                if success:
                    return jsonify({
                        'message': 'Test email sent successfully (synchronous)',
                        'recipient': recipient,
                        'status': 'sent'
                    }), 200
                else:
                    return jsonify({
                        'message': 'Failed to send test email',
                        'error': 'Check email configuration'
                    }), 500
                    
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @app.route('/api/send-mail', methods=['POST'])
    def send_mail_via_celery():
        """Send an email using Celery background task"""
        data = request.get_json()
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        if not to or not subject or not body:
            return jsonify({'error': 'Missing to, subject, or body'}), 400
        from application.tasks import send_email_task
        send_email_task.delay(to, subject, body)
        return jsonify({'message': f'Email task submitted for {to}'}), 200
    
    # ==================== HEALTH CHECK ====================
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({'message': 'API is running', 'status': 'healthy'}), 200