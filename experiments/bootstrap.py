import sys
import os
import configparser

config = configparser.ConfigParser()
config.read('../shothammer_config.ini')
SGHS_NAME = config['shothammer']['SGHS_NAME']
SGHS_KEY = config['shothammer']['SGHS_KEY']

# insert the correct path for sgtk
sys.path.insert(0, "C:/shotgrid-hammerspace/tk-core/python")
import sgtk

def project_id_from_event(event=None) -> int:
    if not event:
        return None
    return event['project']['id']

sgtk.LogManager().initialize_custom_handler()
sgtk.LogManager().global_debug = False

sa = sgtk.authentication.ShotgunAuthenticator()
# Create a user object
user = sa.create_script_user(api_script=SGHS_NAME,
                             api_key=SGHS_KEY,
                             host=os.environ['SG_ED_SITE_URL'])
sgtk.set_authenticated_user(user)

# Re-bootstrap the engine under the correct context...
mgr = sgtk.bootstrap.ToolkitManager(sgtk.get_authenticated_user())
mgr.plugin_id = "sghs."
# mgr.pipeline_configuration = 'distro_rez'

print("here is the manager object:")
print(mgr)

# Now that we've got an initial sgtk bootstrap we should be able to pull per-project configs
# the below needs to be in the callback function so that it gets called for every matching event
# Get the project id from the event
# project_id = project_id_from_event(event)
# project_id = 952
# shot_id = 9583
shot_id = 9502
# bootstrap the specific project
print("trying to bootstrap shot ID %s" % shot_id)
# engine = mgr.bootstrap_engine("tk-shell", entity={"type": "Project", "id": project_id})
engine = mgr.bootstrap_engine("tk-shell", entity={"type": "Shot", "id": shot_id})

# now we're bootstrapped, we can do what we need to do
print("here is the engine object: %s" % str(engine))

# Get the work_shot_area_template from the new engine.sgtk
work_shot_area_template = engine.sgtk.templates["work_shot_area"]

print("work_shot_area_template:\n%s" % str(work_shot_area_template))

print("work_shot_area_template.keys:\n%s" % str(work_shot_area_template.keys))
print("work_shot_area_template.definition:\n%s" % str(work_shot_area_template.definition))

# set up the filter and the fields to pass to find_one
filters = [["id", "is", shot_id]]
fields = ["id", "type", "code", "sg_episode", "sg_sequence"]

# get full_shot
full_shot = engine.shotgun.find_one("Shot", filters=filters, fields=fields)

print("full_shot:\n%s" % str(full_shot))
Shot = full_shot['code']
Sequence = full_shot['sg_sequence']
Episode = full_shot['sg_episode']['name']

# apply_fields to get the whole path
print("work_shot_area_template.apply_fields():\n%s" %
str(work_shot_area_template.apply_fields({'Shot':Shot,
                                        'Sequence':Sequence,
                                        'Episode':Episode,
                                        })))
# print(work_shot_area_template.apply_fields({'Episode':'ep888', 'Shot':'sh0000'}))

# fields = project_context.as_template_fields(work_shot_area_template)
# fields = engine.context.as_template_fields(work_shot_area_template)
# print(fields)

# now we're done, so we can destroy the engine and await another callback
engine.destroy()