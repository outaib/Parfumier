from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required
from bson.objectid import ObjectId
from app import mongo
from app.typesBP.forms import CreateTypeForm, EditTypeForm


typesBP = Blueprint("typesBP", __name__)


@typesBP.route("/type/new", methods=["POST", "GET"])
@login_required
def new_type():
    if current_user.is_admin:
        form = CreateTypeForm()
        if form.validate_on_submit():
            mongo.db.types.insert(
                {
                    "type_name": form.type_name.data,
                    "description": form.description.data,
                    "author": current_user.username,
                }
            )
            flash("You added a new type!", "info")
            return redirect(url_for("typesBP.types"))
    else:
        flash("You need to be an administrator.", "danger")
        return redirect(url_for("mainBP.index"))
    return render_template("pages/new_type.html", title="New Type", form=form)


@typesBP.route("/types")
def types():
    types = mongo.db.types.find().sort("type_name")
    return render_template("pages/types.html", types=types)


@typesBP.route("/type/<id>")
def type(id):
    type = mongo.db.types.find_one({"_id": ObjectId(id)})
    return render_template("pages/type.html", type=type)


@typesBP.route("/type/<id>", methods=["POST"])
@login_required
def delete_type(id):
    if current_user.is_admin:
        mongo.db.types.delete_one({"_id": ObjectId(id)})
        flash("You deleted this type", "success")
        return redirect(url_for("typesBP.types"))
    flash("Not allowed", "warning")
    return redirect(url_for("typesBP.types"))


@typesBP.route("/type/edit/<id>", methods=["POST", "GET"])
@login_required
def edit_type(id):
    form = EditTypeForm()
    current_type_name = mongo.db.types.find_one(
        {"_id": ObjectId(id)}, {"_id": 0, "type_name": 1}
    )
    form.origin_type_name.data = current_type_name["type_name"]
    type = mongo.db.types.find_one({"_id": ObjectId(id)})
    if current_user.is_admin:
        if form.validate_on_submit():
            new_value = {
                "$set": {
                    "type_name": form.type_name.data,
                    "description": form.description.data,
                }
            }
            mongo.db.types.update_one(type, new_value)
            flash("Type has been updated", "info")
            return redirect(url_for("typesBP.type", id=type["_id"]))
        elif request.method == "GET":
            form.type_name.data = type["type_name"]
            form.description.data = type["description"]
    return render_template("pages/edit_type.html", title="Edit Type", form=form)
