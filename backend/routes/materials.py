from flask import Blueprint, jsonify, request, send_file, current_app, Response
from functools import wraps
from models.user import db, User
from models.material import Material
from utils.security import verify_token
import os
import uuid
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint("materials", __name__)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf'}

def get_upload_folder(component_name=None):
    """获取上传文件夹路径，按知识点分类"""
    base_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'materials')
    
    if component_name and component_name != 'other':
        # 按知识点分类存储
        upload_folder = os.path.join(base_folder, component_name)
    else:
        # 其他文件存储在others文件夹
        upload_folder = os.path.join(base_folder, 'others')
    
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"code": 401, "message": "未提供认证令牌"}), 401
        
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"code": 401, "message": "无效的认证令牌"}), 401
            request.user_id = user_id
            request.current_user = User.query.get(user_id)
        except Exception as e:
            return jsonify({"code": 401, "message": f"认证失败: {str(e)}"}), 401
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user:
            return jsonify({"code": 401, "message": "未认证"}), 401
        if not request.current_user.is_admin:
            return jsonify({"code": 403, "message": "需要管理员权限"}), 403
        return f(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    try:
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in ALLOWED_EXTENSIONS
    except (IndexError, AttributeError):
        return False


@bp.route("/materials", methods=["GET"])
@login_required
def list_materials():
    """获取资料列表"""
    try:
        component_name = request.args.get("component_name", "")  # 按组件筛选
        is_admin = request.current_user.is_admin if request.current_user else False
        
        query = Material.query.filter_by(is_active=True)
        
        # 如果不是管理员，只能查看与当前学习路径相关的资料
        # 这里可以根据实际需求调整筛选逻辑
        if component_name:
            query = query.filter_by(component_name=component_name)
        
        materials = query.order_by(Material.created_at.desc()).all()
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": [material.to_dict() for material in materials]
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/materials/<int:material_id>", methods=["GET"])
@login_required
def get_material(material_id):
    """获取资料详情"""
    try:
        material = Material.query.get_or_404(material_id)
        
        if not material.is_active:
            return jsonify({"code": 404, "message": "资料不存在"}), 404
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": material.to_dict()
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/materials/<int:material_id>/download", methods=["GET"])
@login_required
def download_material(material_id):
    """下载资料文件"""
    try:
        from flask import Response
        
        material = Material.query.get_or_404(material_id)
        
        if not material.is_active:
            return jsonify({"code": 404, "message": "资料不存在"}), 404
        
        # 根据component_name确定文件路径
        component_name = material.component_name if material.component_name else None
        file_path = os.path.join(get_upload_folder(component_name), material.file_path)
        if not os.path.exists(file_path):
            return jsonify({"code": 404, "message": "文件不存在"}), 404
        
        # 使用title作为下载文件名，如果没有title则使用file_name
        download_filename = material.title or material.file_name or '资料'
        if not download_filename.lower().endswith('.pdf'):
            download_filename = download_filename + '.pdf'
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 对文件名进行URL编码，确保中文文件名正确显示
        import urllib.parse
        # 使用ASCII安全的文件名（用于兼容性）
        safe_filename = download_filename.encode('ascii', 'ignore').decode('ascii')
        if not safe_filename or safe_filename != download_filename:
            # 如果包含非ASCII字符，使用编码后的文件名
            encoded_filename = urllib.parse.quote(download_filename.encode('utf-8'))
            content_disposition = f"attachment; filename*=UTF-8''{encoded_filename}"
        else:
            # 如果只有ASCII字符，直接使用
            content_disposition = f'attachment; filename="{safe_filename}"'
        
        # 创建响应，确保文件完整传输
        response = Response(
            file_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': content_disposition,
                'Content-Length': str(len(file_data)),
                'Content-Type': 'application/pdf'
            }
        )
        
        return response
    except Exception as e:
        return jsonify({"code": 500, "message": f"下载失败: {str(e)}"}), 500


@bp.route("/materials", methods=["POST"])
@login_required
@admin_required
def create_material():
    """创建资料（仅管理员）"""
    try:
        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "")
        # 安全处理 component_name，可能是 None、空字符串或 'other'
        component_name_raw = data.get("component_name")
        if component_name_raw:
            component_name = component_name_raw.strip() if isinstance(component_name_raw, str) else None
        else:
            component_name = None
        
        # 处理'other'选项
        if component_name == 'other' or not component_name:
            component_name = None
        
        file_path = data.get("file_path", "")  # 如果通过上传接口上传，这里会传入路径
        
        if not title:
            return jsonify({"code": 400, "message": "资料标题不能为空"}), 400
        
        if not file_path:
            return jsonify({"code": 400, "message": "文件路径不能为空"}), 400
        
        material = Material(
            title=title,
            description=description,
            file_path=file_path,
            file_name=data.get("file_name", ""),
            file_size=data.get("file_size", 0),
            file_type=data.get("file_type", "pdf"),
            component_name=component_name,
            created_by=request.user_id,
            is_active=True
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "创建成功",
            "data": material.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"创建失败: {str(e)}"}), 500


@bp.route("/materials/upload", methods=["POST"])
@login_required
@admin_required
def upload_material():
    """上传资料文件（仅管理员），支持按知识点分类存储"""
    """上传资料文件（仅管理员）"""
    try:
        if 'file' not in request.files:
            return jsonify({"code": 400, "message": "未选择文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"code": 400, "message": "未选择文件"}), 400
        
        # 先检查原始文件名
        original_filename = file.filename
        if not allowed_file(original_filename):
            return jsonify({"code": 400, "message": "只支持PDF文件"}), 400
        
        # 从原始文件名提取扩展名（在secure_filename处理之前）
        if '.' not in original_filename:
            return jsonify({"code": 400, "message": "文件名缺少扩展名"}), 400
        
        try:
            file_ext = original_filename.rsplit('.', 1)[1].lower()
        except IndexError:
            return jsonify({"code": 400, "message": "无法解析文件扩展名"}), 400
        
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({"code": 400, "message": "只支持PDF文件"}), 400
        
        # 获取组件名称（从请求参数中获取，用于分类存储）
        component_name = request.form.get('component_name', 'other')
        if component_name == 'other' or not component_name:
            component_name = None
        
        # 生成唯一文件名：仅使用uuid
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # 保存原始文件名用于显示
        safe_filename = secure_filename(original_filename)
        # 如果secure_filename移除了扩展名，我们手动添加回去
        if '.' not in safe_filename:
            # 从原始文件名获取文件名部分（不含扩展名）
            name_part = original_filename.rsplit('.', 1)[0]
            safe_filename = secure_filename(name_part) + '.' + file_ext
        
        # 按知识点分类存储
        upload_folder = get_upload_folder(component_name)
        file_path = os.path.join(upload_folder, unique_filename)
        
        # 保存文件
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        return jsonify({
            "code": 200,
            "message": "上传成功",
            "data": {
                "file_path": unique_filename,
                "file_name": safe_filename,
                "file_size": file_size,
                "file_type": file_ext
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"上传失败: {str(e)}"}), 500


@bp.route("/materials/<int:material_id>", methods=["PUT"])
@login_required
@admin_required
def update_material(material_id):
    """更新资料（仅管理员），如果关联知识点改变，移动文件到对应文件夹"""
    try:
        material = Material.query.get_or_404(material_id)
        data = request.get_json()
        
        old_component_name = material.component_name
        
        if "title" in data:
            material.title = data["title"].strip()
        if "description" in data:
            material.description = data.get("description", "")
        if "component_name" in data:
            comp_name = data["component_name"].strip() if data["component_name"] else None
            # 处理'other'选项
            if comp_name == 'other' or not comp_name:
                material.component_name = None
            else:
                material.component_name = comp_name
        if "is_active" in data:
            material.is_active = data["is_active"]
        
        # 如果关联知识点改变，移动文件到对应文件夹
        new_component_name = material.component_name
        if old_component_name != new_component_name:
            old_folder = get_upload_folder(old_component_name)
            new_folder = get_upload_folder(new_component_name)
            old_file_path = os.path.join(old_folder, material.file_path)
            new_file_path = os.path.join(new_folder, material.file_path)
            
            if os.path.exists(old_file_path):
                # 确保目标目录存在
                os.makedirs(new_folder, exist_ok=True)
                # 如果目标文件已存在，先删除
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                # 移动文件
                shutil.move(old_file_path, new_file_path)
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "更新成功",
            "data": material.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@bp.route("/materials/<int:material_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_material(material_id):
    """删除资料（仅管理员）"""
    try:
        material = Material.query.get_or_404(material_id)
        
        # 删除文件（需要根据component_name确定文件路径）
        component_name = material.component_name if material.component_name else None
        file_path = os.path.join(get_upload_folder(component_name), material.file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "删除成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500


@bp.route("/materials/components", methods=["GET"])
@login_required
def list_components():
    """获取所有可用的组件名称列表（从学习路径节点获取）"""
    try:
        from models.learning_path import LearningPathNode
        
        # 从学习路径节点获取所有不同的节点名称（作为组件名称）
        nodes = db.session.query(LearningPathNode.node_name).distinct().filter(
            LearningPathNode.node_name.isnot(None)
        ).all()
        
        component_list = [node[0] for node in nodes if node[0]]
        
        # 同时包含BaseFoundationPath中预定义的组件ID
        predefined_components = [
            {'id': 'network-basics', 'name': '网络基础'},
            {'id': 'linux-basics', 'name': 'Linux基础'},
            {'id': 'windows-basics', 'name': 'Windows基础'},
            {'id': 'security-concepts', 'name': '安全基本概念'}
        ]
        
        # 合并预定义组件和从数据库获取的节点
        result = []
        for comp in predefined_components:
            result.append({
                'id': comp['id'],
                'name': comp['name']
            })
        
        # 添加从数据库获取的节点（排除已存在的）
        existing_ids = [c['id'] for c in result]
        for node_name in component_list:
            # 如果节点名称不在预定义列表中，也添加进去
            if node_name not in existing_ids:
                result.append({
                    'id': node_name,
                    'name': node_name
                })
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": result
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500
