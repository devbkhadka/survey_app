window.survey_app = {
    initialize: function(){
        jQuery("#btn-next").on("click", function(_e){
            form = jQuery("#question_form")
            if(form.length == 0){
                return true
            }
            _e.preventDefault()
            form.submit()
        })
       
    }
}
window.survey_app.initialize()