function updateAppointment() {
  if ($('#id_appt').find('option[selected]').val() == 'Yes') {
    $('#div_id_appt_date').show();
    $('#div_id_appt_grading').show();  
    $('#div_id_appt_location').show();
    $('#id_appt_date').prop( "required", true );
    $('#id_appt_grading').prop( "required", true );  
    $('#id_appt_location').prop( "required", true );
  } else {
    $('#div_id_appt_date').hide();  
    $('#div_id_appt_grading').hide();  
    $('#div_id_appt_location').hide();
    $('#div_id_appt_location_other').hide();
    $('#id_appt_date').prop( "required", false );
    $('#id_appt_grading').prop( "required", false );  
    $('#id_appt_location').prop( "required", false );
  };
  $('#id_appt').change( function(e) {
    if (this.value == 'Yes') {
      $('#div_id_appt_date').show();
      $('#div_id_appt_grading').show();  
      $('#div_id_appt_location').show();
      $('#id_appt_date').prop( "required", true );
      $('#id_appt_grading').prop( "required", true );  
      $('#id_appt_location').prop( "required", true );
    } else {
      $('#div_id_appt_date').hide();  
      $('#div_id_appt_grading').hide();  
      $('#div_id_appt_location').hide();
      $('#div_id_appt_location_other').hide();
      $('#id_appt_date').prop( "required", false );
      $('#id_appt_grading').prop( "required", false );  
      $('#id_appt_location').prop( "required", false );
      $('#id_appt_location_other').prop( "required", false );
    }        
  });
  if ($('#id_appt_location').find('option[selected]').val() == 'OTHER') {
    $('#div_id_appt_location_other').show();
    $('#id_appt_location_other').prop( "required", true );  
  } else {
    $('#div_id_appt_location_other').hide();
    $('#id_appt_location_other').prop( "required", false );  
  };
  $('#id_appt_location').change( function(e) {
    if (this.value == 'OTHER') {
      $('#div_id_appt_location_other').show();  
      $('#id_appt_location_other').prop( "required", true );  
    } else {
      $('#div_id_appt_location_other').hide();
      $('#id_appt_location_other').prop( "required", false );  
    }        
  });
}

function updateContacted() {
   initial_value = $('#id_contact_type').find('option[selected]').val();
  if (initial_value == 'direct' || initial_value == 'indirect') {
    $('#div_id_time_of_week').show().prop( "required", true );  
    $('#div_id_time_of_day').show().prop( "required", true );
    $('#div_id_appt').show().prop( "required", true );
    $('#div_id_may_call').show().prop( "required", true );
  } else {
    $('#div_id_time_of_week').hide().prop( "required", false );
    $('#div_id_time_of_day').hide().prop( "required", false );
    $('#div_id_appt').hide().prop( "required", false );
    $('#div_id_appt_grading').hide().prop( "required", false );
    $('#div_id_appt_date').hide().prop( "required", false );
    $('#div_id_appt_location').hide().prop( "required", false );
    $('#div_id_appt_location_other').hide().prop( "required", false );
    $('#div_id_may_call').hide().prop( "required", false );
  };
  $('#id_contact_type').change( function(e) {
    if (this.value == 'direct' || this.value == 'indirect') {
      $('#div_id_time_of_week').show();  
      $('#div_id_time_of_day').show();
      $('#div_id_appt').show();
      $('#div_id_may_call').show();
      $('#id_time_of_week').prop( "required", true );
      $('#id_time_of_day').prop( "required", true );
      $('#id_appt').prop( "required", true );
      $('#id_may_call').prop( "required", true );
    } else {
      $('#div_id_time_of_week').hide().prop( "required", false );
      $('#div_id_time_of_day').hide().prop( "required", false );
      $('#div_id_appt').hide().prop( "required", false );
      $('#div_id_appt_grading').hide().prop( "required", false );
      $('#div_id_appt_date').hide().prop( "required", false );
      $('#div_id_appt_location').hide().prop( "required", false );
      $('#div_id_appt_location_other').hide().prop( "required", false );
      $('#div_id_may_call').hide().prop( "required", false );
    }
  });
}